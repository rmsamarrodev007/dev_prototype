from flask import Flask, render_template, jsonify, request
from flask import Flask, render_template,jsonify, request, redirect, url_for, session, flash
from connection import db
from datetime import datetime, time
from threading import Thread
import webview
import configparser

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'thisisasecretkey'
LATE_TIME_HOUR = 7
LATE_TIME_MINUTE = 15

users = {
    'admin': {'password': 'admin123', 'role': 'admin'},
    'user': {'password': 'user123', 'role': 'user'}
}

@app.route("/")
def index():
    # if 'username' in session:
    return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        return render_template("login.html")

    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username', None)
        password = data.get('password', None)
        # username = request.form['username']
        # password = request.form['password']
        print(f"{username}:{password}")
        # Check if username exists in the "database"
        # Check if the username exists and the password matches
        if username in users and users[username]['password'] == password:
            session['username'] = username  # Store username in session
            data = jsonify({"success": True, "message": f"Login Successfully"})
            return data
        else:
            # flash('Invalid password. Please try again.', 'danger')
            data = jsonify({"success": True, "message": f"Incorrect username or password."})
            return data

@app.route('/logout')
def logout():
    # Log out the user by removing session data
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/restricted')
def restricted():
    # Check if the user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    # Check if the user has 'admin' role
    if users[session['username']]['role'] != 'admin':
        return "You do not have permission to access this page."
    
    return render_template('restricted_page.html')

@app.route("/dashboard")
def dashboard():
    if 'username' in session:
        nonactive = db.get_employee_count(is_not_active=True)
        active = db.get_employee_count(is_not_active=False)
        total_salary = db.get_total_emp_salary()
        employees = db.get_all_employees()
        return render_template("dashboard.html", active=active, nonactive=nonactive, total_salary=total_salary, employees=employees )
    return render_template('restricted_page.html')

@app.route("/payslip", methods=['GET'])
def payslip():
    if 'username' in session:
        if request.method == 'GET':
            id = int(request.args.get("id", 0))
            start_date = request.args.get("start_date", 0)
            end_date = request.args.get("end_date", 0)
            employee = db.get_employee_by_id(id)
            time_card = db.get_timecard_by_emp(id, start_date, end_date)
            total_daily_rate = 0
            total_ot_pay = 0
            total_earnings = 0
            total_deductions = 0
            list_total_daily_rate = []

            # start_date_name = time_card[0][7].strftime('%d %B %Y')
            # end_date_name = time_card[len(time_card)-1][7].strftime('%d %B %Y')

            payroll = db.get_timecard_min_max(id, start_date)
            print(f"payroll:{payroll}")
            start_date_name = payroll[0].strftime('%d %B %Y')
            end_date_name = payroll[1].strftime('%d %B %Y')

            now = datetime.now()
            date_now = now.strftime('%d %B %Y')

            for tc in time_card:
                if tc[2] is not None and tc[3] is not None:
                    login_time = datetime.strptime(str(tc[2].strftime("%H:%M")), "%H:%M").time()
                    login_date_time = datetime.strptime(str(tc[2].strftime("%Y-%m-%d %H:%M")), "%Y-%m-%d %H:%M")
                    late_time = time(int(LATE_TIME_HOUR), int(LATE_TIME_MINUTE))
                    late_date_time = datetime.strptime(f"""{str(tc[2].strftime("%Y-%m-%d"))} {LATE_TIME_HOUR}:{LATE_TIME_MINUTE}""", "%Y-%m-%d %H:%M")
                    
                # login_time = datetime.strptime(str(tc[2].strftime("%H:%M")), "%H:%M").time()
                # login_date_time = datetime.strptime(str(tc[2].strftime("%Y-%m-%d %H:%M")), "%Y-%m-%d %H:%M")
                # late_time = time(int(LATE_TIME_HOUR), int(LATE_TIME_MINUTE))
                # late_date_time = datetime.strptime(f"""{str(tc[2].strftime("%Y-%m-%d"))} {LATE_TIME_HOUR}:{LATE_TIME_MINUTE}""", "%Y-%m-%d %H:%M")
                
                    #validate late login @ 7:15 onwards
                    if login_time > late_time:

                        time_diff = login_date_time - late_date_time
                        total_seconds = time_diff.total_seconds()
                        hours = total_seconds // 3600
                        minutes = (total_seconds % 3600) // 60

                        hourly_rate = employee[0][4] / 8
                        minute_rate = hourly_rate / 60
                        late_deduction = minutes * float(minute_rate)
                        total_deductions += late_deduction

                    ot_rendered = 0
                    worked_hours = 0
                    ot_pay = 0
                    if tc[2] is not None and tc[3] is not None:
                        time_in = datetime.strptime(str(tc[2].strftime("%H:%M")), "%H:%M")
                        time_out = datetime.strptime(str(tc[3].strftime("%H:%M")), "%H:%M")
                        # Calculate the difference between time_out and time_in
                        time_diff = time_out - time_in
                        total_seconds = time_diff.total_seconds()
                        hours = total_seconds // 3600
                        minutes = (total_seconds % 3600) // 60
                        worked_hours = float(f"{int(hours)}.{int(minutes)}")

                        # if worked_hours > 9:
                        #     ot_rate = 1.25
                        #     ot_rendered = worked_hours - 9
                        #     ot_pay = (float(employee[0][4]) / 8) * ot_rate
                        #     ot_pay = ot_pay * ot_rendered
                        #     total_ot_pay += ot_pay

                        # total_daily_rate += employee[0][4]
                        if worked_hours > 9:
                            ot_rate = 1.25
                            ot_rendered = worked_hours - 9
                            ot_pay = (float(employee[0][4]) / 8) * ot_rate
                            ot_pay = ot_pay * ot_rendered
                            total_ot_pay += ot_pay
                            list_total_daily_rate.append(employee[0][4])
                        else:
                            if worked_hours == 5.0:
                                list_total_daily_rate.append(employee[0][4] / 2)
                            else:
                                list_total_daily_rate.append(employee[0][4])

                        # if worked_hours == 5.0:
                        #     emp_daily_rate = employee[0][4] / 2
                        # else:
                        #     emp_daily_rate = employee[0][4]

                        if worked_hours != 0:
                            worked_hours = worked_hours - 1 
                        else:
                            worked_hours = 0
            total_daily_rate = sum(list_total_daily_rate)
            print(f"total_daily_rate:{total_daily_rate}")
            total_earnings = (float(total_daily_rate) + total_ot_pay) - total_deductions
            basic_salary = employee[0][4] * 26

            return render_template("payslip.html",
                employee=employee[0],
                basic_salary=f"{basic_salary:.2f}",
                total_ot_pay=f"{total_ot_pay:.2f}",
                total_daily_rate=f"{total_daily_rate:.2f}",
                total_earnings= f"{total_earnings:.2f}",
                start_date_name=start_date_name,
                end_date_name=end_date_name,
                date_now=date_now,
                total_deductions=f"{total_deductions:.2f}"
                )

    return render_template('restricted_page.html')

@app.route("/list_time_card_per_emp", methods=["GET", "POST"])
def list_time_card_per_emp():
    print("METHOD:")
    print(request.method)
    if 'username' in session:
        if request.method == "GET":
            id = int(request.args.get("id", 0))
            start_date = request.args.get("start_date", None)
            end_date = request.args.get("end_date", None)

            print(start_date, end_date)
            # time_card = db.get_timecard_by_emp(id)
            time_card = db.get_timecard_by_emp(id, start_date, end_date)
            employee = db.get_employee_by_id(id)
            list_time_card = []
            total_daily_rate = 0
            total_ot_pay = 0
            total_earnings = 0
            total_deductions = 0
            list_total_daily_rate = []
            
            is_late = False
            
            for tc in time_card:
                worked_hours = 0
                ot_rendered = 0
                ot_pay = 0
                
                if tc[2] is not None and tc[3] is not None:
                    login_time = datetime.strptime(str(tc[2].strftime("%H:%M")), "%H:%M").time()
                    login_date_time = datetime.strptime(str(tc[2].strftime("%Y-%m-%d %H:%M")), "%Y-%m-%d %H:%M")
                    late_time = time(int(LATE_TIME_HOUR), int(LATE_TIME_MINUTE))
                    late_date_time = datetime.strptime(f"""{str(tc[2].strftime("%Y-%m-%d"))} {LATE_TIME_HOUR}:{LATE_TIME_MINUTE}""", "%Y-%m-%d %H:%M")
                    
                    #validate late login @ 7:15 onwards
                    if login_time > late_time:
                        is_late = True
                        time_diff = login_date_time - late_date_time
                        total_seconds = time_diff.total_seconds()
                        hours = total_seconds // 3600
                        minutes = (total_seconds % 3600) // 60

                        hourly_rate = employee[0][4] / 8
                        minute_rate = hourly_rate / 60
                        late_deduction = minutes * float(minute_rate)
                        print(f"late_deduction:{late_deduction}")

                        total_deductions += late_deduction
                    else:
                        is_late = False

                    time_in = datetime.strptime(str(tc[2].strftime("%H:%M")), "%H:%M")
                    time_out = datetime.strptime(str(tc[3].strftime("%H:%M")), "%H:%M")
                    # time_in = datetime.strptime(str(tc[2].strftime("%Y-%m-%d %H:%M")), "%Y-%m-%d %H:%M")
                    # time_out = datetime.strptime(str(tc[3].strftime("%Y-%m-%d %H:%M")), "%Y-%m-%d %H:%M")
                    
                    # Calculate the difference between time_out and time_in
                    time_diff = time_out - time_in
                    total_seconds = time_diff.total_seconds()
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    worked_hours = float(f"{int(hours)}.{int(minutes)}")
                    # print(f"worked_hours:{worked_hours, id}")
                    if worked_hours > 9:
                        ot_rate = 1.25
                        ot_rendered = worked_hours - 9
                        ot_pay = (float(employee[0][4]) / 8) * ot_rate
                        ot_pay = ot_pay * ot_rendered
                        total_ot_pay += ot_pay
                        list_total_daily_rate.append(employee[0][4])
                    else:
                        if worked_hours == 5.0:
                            list_total_daily_rate.append(employee[0][4] / 2)
                        else:
                            list_total_daily_rate.append(employee[0][4])

                    if worked_hours == 5.0:
                        emp_daily_rate = employee[0][4] / 2
                    else:
                        emp_daily_rate = employee[0][4]

                    if worked_hours != 0:
                        worked_hours = worked_hours - 1 
                    else:
                        worked_hours = 0

                total_daily_rate = sum(list_total_daily_rate)
                total_earnings = (float(total_daily_rate) + total_ot_pay) - total_deductions
                
            

                tc_map = {
                    "time_card_id": tc[0],
                    "employee_id": tc[1],
                    "date": tc[7],
                    "time_in": tc[2].strftime("%Y-%m-%d %H:%M") if tc[2] is not None else tc[2],
                    "time_out": tc[3].strftime("%Y-%m-%d %H:%M") if tc[3] is not None else tc[3],
                    "worked_hours": f"{worked_hours:.2f}",
                    "ot_rendered": f"{ot_rendered:.2f}",
                    "ot_pay": f"{ot_pay:.2f}" if (tc[4] == 'Present' and tc[2] is not None)  else 0,
                    "remarks": tc[4],
                    "note": tc[5],
                    "daily_rate": f"{emp_daily_rate:.2f}" if (tc[4] == 'Present' and tc[2] is not None) else 0,
                    "late": f"{late_deduction:.2f}" if is_late else 0
                }
                list_time_card.append(tc_map)
            
            print(f"total_daily_rate:{total_daily_rate}")
            basic_salary = employee[0][4] * 6
            hourly_rate = employee[0][4] / 8

            return render_template(
                "list_time_card_per_emp.html",
                time_cards=list_time_card,
                employee=employee[0],
                basic_salary=f"{basic_salary:.2f}",
                hourly_rate=f"{hourly_rate:.2f}",
                total_ot_pay=f"{total_ot_pay:.2f}",
                total_daily_rate=f"{total_daily_rate:.2f}",
                total_earnings= f"{total_earnings:.2f}",
                total_deductions= f"{total_deductions:.2f}"
            )

        if request.method == "POST":
            # Get the incoming JSON data (which contains the ID of the item to delete)
            data = request.get_json()
            tc_id = data.get('id', 0)
            start_date = data.get('start_date', None)
            end_date = data.get('end_date', None)

            if tc_id != 0 and start_date is None:
                print("update time card")
                db.update_time_card(tc_id)
                # Respond with a success message
                return jsonify({"success": True, "message": f"Item {tc_id} deleted successfully."})

            if start_date is not None and end_date is not None:
                return jsonify({"success": True, "message": f"start date: {start_date} and end_date: {end_date}"})
    return render_template('restricted_page.html')

@app.route("/list_of_employees", methods=["GET", "POST"])
def list_of_employees():
    if 'username' in session:
        if request.method == "GET":
            employees = db.get_all_active_employees()
            return render_template("list_of_employees.html", employees=employees)

        if request.method == "POST":
            # Get the incoming JSON data (which contains the ID of the item to delete)
            data = request.get_json()
            emp_id = data.get('id')
            db.update_employee(emp_id)
            # Respond with a success message
            return jsonify({"success": True, "message": f"Item {emp_id} deleted successfully."})
    return render_template('restricted_page.html')

@app.route("/add_time_card_per_emp", methods=["GET", "POST"])
def add_time_card_per_emp():
    if 'username' in session:
        if request.method == "GET":
            id = int(request.args.get("id"))
            employee = db.get_employee_by_id(id)
            return render_template("add_time_card_per_emp.html", employee=employee[0])

        if request.method == "POST":
            id = request.form["hid_emp_id"]
            remarks = request.form["remarks"]
            login_date = request.form["login_date"]
            print(f"login_date: {id}")
            logout_date = request.form["logout_date"]

            note = request.form["note"]

            results = db.add_time_card(id, login_date, logout_date, remarks, note)
            print(f"results: {results}")
            employee = db.get_employee_by_id(id)

            if results:
                # Display results
                return render_template(
                    "add_time_card_per_emp.html", remarks=remarks, employee=employee[0]
                )
    return render_template('restricted_page.html')

# Calculate payroll
@app.route("/add_employee", methods=["GET", "POST"])
def add_employee():
    if 'username' in session:
        try:
            if request.method == "GET":
                return render_template("add_employee.html")

            if request.method == "POST":
                status = "Active"
                # Get form data
                employee_name = request.form["employee_name"]
                employee_type = request.form["employee_type"]
                daily_rate = float(request.form["daily_rate"])

                results = db.add_employee(employee_name, employee_type, status, daily_rate)

                if results:
                    # Display results
                    return render_template(
                        "add_employee.html",
                        employee_name=employee_name,
                        employee_type=employee_type,
                        daily_rate=daily_rate,
                    )
        except ValueError:
            return render_template("add_employee.html", error="Please enter valid numbers.")
    return render_template('restricted_page.html')


# if __name__ == "__main__":
#     # app.run(debug=True)
#     # app.run(host='0.0.0.0', port=5000)
#     webview.start()

# Function to run the Flask app in a separate thread
def run_flask():
    app.run(host='127.0.0.1', port=5000)

# Start Flask in a background thread and open the WebView
def start_webview():
    # Start Flask server in a separate thread
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Create the WebView window and load the Flask app URL
    webview.create_window('Payroll Application', 'http://127.0.0.1:5000', width=1400, height=700)
    webview.start()

if __name__ == '__main__':
    # start_webview()
    app.run(debug=True)

# https://www.pythonanywhere.com/user/samarrors/webapps/#tab_id_samarrors_pythonanywhere_com