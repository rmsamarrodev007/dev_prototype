from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

# Example in-memory database (For production, replace with an actual database)
employees = []

@app.route('/')
def index():
    return render_template('index.html', employees=employees)

@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        name = request.form['name']
        salary = float(request.form['salary'])
        tax_deductions = float(request.form['tax_deductions'])
        bonus = float(request.form['bonus'])
        net_salary = salary - tax_deductions + bonus

        employee = {
            'name': name,
            'salary': salary,
            'tax_deductions': tax_deductions,
            'bonus': bonus,
            'net_salary': net_salary
        }
        employees.append(employee)
        return redirect(url_for('index'))

    return render_template('add_employee.html')

@app.route('/payroll_slip/<int:employee_id>')
def payroll_slip(employee_id):
    employee = employees[employee_id]
    return render_template('payroll_slip.html', employee=employee)

if __name__ == '__main__':
    app.run(debug=True)
