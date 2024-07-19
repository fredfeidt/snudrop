from flask import Flask, render_template, request, redirect, url_for, jsonify
import os, ast

app = Flask(__name__)

@app.route('/')
def home():
    return redirect(url_for('stock'))

@app.route('/stock')
def stock():
    directory_path = 'instance/stock'
    stock = []
    total_units = 0

    for filename in os.listdir(directory_path):
        temp = []
        file_path = os.path.join(directory_path, filename)
    
        if os.path.isfile(file_path):
            name, extension = os.path.splitext(filename)
            temp.append(name)

            with open(file_path, 'r') as file:
                content = file.read().strip()
                current_quantity = int(content) if content else 0
                temp.append(f"{current_quantity}")
                new_total_units = total_units + current_quantity
                total_units = new_total_units
        
        stock.append(temp)
    
    return render_template('stock.html', stock=stock, total_units=total_units)

@app.route('/add_stock_item', methods=['POST'])
def add_stock_item():
    name = request.json.get('name')
    quantity = int(request.json.get('quantity'))

    file_name = f"instance/stock/{name}.txt"

    if os.path.exists(file_name):
        with open(file_name, 'r') as file:
            content = file.read().strip()
            current_quantity = int(content) if content else 0

        new_quantity = quantity + current_quantity

        with open(file_name, 'w') as file:
            file.write(f"{new_quantity}")
    else:
        with open(file_name, 'w') as file:
            file.write(f"{quantity}")

    return jsonify(success=True)

@app.route('/delete_stock_item', methods=['POST'])
def delete_stock_item():
    item_id = request.json.get('item_id')
    file_path = f"instance/stock/{item_id}.txt"
    if os.path.isfile(file_path):
        os.remove(file_path)
        return jsonify(success=True)
    else:
        return jsonify(success=False, error="Stock item not found")

@app.route('/sales')
def sales():
    directory_path = 'instance/stock'
    items = []
    total_profit = 0

    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
    
        if os.path.isfile(file_path):
            name, extension = os.path.splitext(filename)
            items.append(name)

    file_path = 'instance/money_log.txt'
    with open(file_path, 'r') as file:
        file_content = file.read()

    imported_list = ast.literal_eval(file_content)
    for item in imported_list:
        new_total_profit = total_profit + item[4]
        total_profit = new_total_profit

    imported_list.reverse()
    
    return render_template('sales.html', sales=imported_list, total_profit=total_profit, items=items)

@app.route('/add_sale', methods=['POST'])
def add_sale():
    item_id = request.json.get('item_id')
    quantity = int(request.json.get('quantity'))
    price = float(request.json.get('price'))

    file_path = f"instance/stock/{item_id}.txt"
    if os.path.isfile(file_path):
        with open(file_path, 'r') as file:
            content = file.read().strip()
            current_quantity = int(content) if content else 0

        if quantity <= current_quantity:
            file_path = "instance/id.txt"
            with open(file_path, 'r') as file:
                content = file.read().strip()
                current_id = int(content) if content else 0

            new_id = current_id + 1

            with open(file_path, 'w') as file:
                file.write(f"{new_id}")

            
            file_path = 'instance/money_log.txt'
            with open(file_path, 'r') as file:
                file_content = file.read()

            imported_list = ast.literal_eval(file_content)
            imported_list.append([new_id, 0, item_id, quantity, price])

            with open(file_path, 'w') as file:
                file.write(str(imported_list))


            file_path = f"instance/stock/{item_id}.txt"
            if os.path.exists(file_path):
                with open(file_path, 'r') as file:
                    content = file.read().strip()
                    current_quantity = int(content) if content else 0

                new_quantity = current_quantity - quantity

                with open(file_path, 'w') as file:
                    file.write(f"{new_quantity}")
        
            return jsonify(success=True)
        
    return jsonify(success=False, error="Insufficient stock")

@app.route('/add_expense', methods=['POST'])
def add_expense():
    name = request.json.get('name')
    price = float(request.json.get('price'))

    file_path = "instance/id.txt"
    with open(file_path, 'r') as file:
        content = file.read().strip()
        current_id = int(content) if content else 0

    new_id = current_id + 1

    with open(file_path, 'w') as file:
        file.write(f"{new_id}")

            
    file_path = 'instance/money_log.txt'
    with open(file_path, 'r') as file:
        file_content = file.read()

    imported_list = ast.literal_eval(file_content)
    imported_list.append([new_id, 1, name, "", 0 - price])

    with open(file_path, 'w') as file:
        file.write(str(imported_list))
    
    return jsonify(success=True)

@app.route('/delete_sale', methods=['POST'])
def delete_sale():
    sale_id = request.json.get('sale_id')
    temp = []
    
    file_path = 'instance/money_log.txt'
    with open(file_path, 'r') as file:
        file_content = file.read()

    imported_list = ast.literal_eval(file_content)
    for item in imported_list:
        if item[0] == sale_id:
            temp = item

    filtered_list = [sublist for sublist in imported_list if sublist[0] != sale_id]

    with open(file_path, 'w') as file:
        file.write(str(filtered_list))

    if temp[1] == 0:
        file_path = f"instance/stock/{temp[2]}.txt"
        with open(file_path, 'r') as file:
            content = file.read().strip()
            current_quantity = int(content) if content else 0

        new_quantity = temp[3] + current_quantity

        with open(file_path, 'w') as file:
            file.write(f"{new_quantity}")

    return jsonify(success=True)

if __name__ == '__main__':
    app.run(debug=False)
