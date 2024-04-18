from flask import Flask, render_template, request
from sqlalchemy import Column, Integer, String, Numeric, create_engine, text

app = Flask(__name__)
conn_str = "mysql://root:100Gecsfan@localhost/boatdb"
engine = create_engine(conn_str, echo=True)
conn = engine.connect()


# render a file
@app.route('/')
def index():
    return render_template('index.html')


# remember how to take user inputs?
@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


# get all boats
# this is done to handle requests for two routes -
@app.route('/boats/')
@app.route('/boats/<page>')
def get_boats(page=1):
    page = int(page)  # request params always come as strings. So type conversion is necessary.
    per_page = 10  # records to show per page
    boats = conn.execute(text(f"SELECT * FROM boats LIMIT {per_page} OFFSET {(page - 1) * per_page}")).all()
    print(boats)
    return render_template('boats.html', boats=boats, page=page, per_page=per_page)


@app.route('/create', methods=['GET'])
def create_get_request():
    return render_template('boats_create.html')


@app.route('/create', methods=['POST'])
def create_boat():
    # you can access the values with request.from.name
    # this name is the value of the name attribute in HTML form's input element
    # ex: print(request.form['id'])
    try:
        conn.execute(
            text("INSERT INTO boats values (:id, :name, :type, :owner_id, :rental_price)"),
            request.form
        )
        return render_template('boats_create.html', error=None, success="Data inserted successfully!")
    except Exception as e:
        error = e.orig.args[1]
        print(error)
        return render_template('boats_create.html', error=error, success=None)


@app.route('/delete', methods=['GET'])
def delete_get_request():
    return render_template('boats_delete.html')


@app.route('/delete', methods=['POST'])
def delete_boat():
    try:
        conn.execute(
            text("DELETE FROM boats WHERE id = :id"),
            request.form
        )
        return render_template('boats_delete.html', error=None, success="Data deleted successfully!")
    except Exception as e:
        error = e.orig.args[1]
        print(error)
        return render_template('boats_delete.html', error=error, success=None)


@app.route('/boat-update/<int:boat_id>', methods=['GET'])
def boat_update_get_request(boat_id):
    boat = conn.execute(text("SELECT * FROM boats WHERE id = :id"), {'id': boat_id}).fetchone()
    if boat:
        return render_template('boat-update.html', boat=boat)
    else:
        return render_template('error.html', message='Boat not found'), 404

@app.route('/boat-update/<int:boat_id>', methods=['POST'])
def boat_update_post_request(boat_id):
    try:
        conn.execute(
            text("UPDATE boats SET name = :name, type = :type, owner_id = :owner_id, rental_price = :rental_price WHERE id = :id"),
            {
                'id': boat_id,
                'name': request.form['name'],
                'type': request.form['type'],
                'owner_id': request.form['owner_id'],
                'rental_price': request.form['rental_price']
            }
        )
        return render_template('boat-update.html', success="Boat information updated successfully!", boat=request.form)
    except Exception as e:
        error = e.orig.args[1]
        print(error)
        return render_template('boat-update.html', error=error, boat=request.form)


@app.route('/search', methods=['GET'])
def search_boats():
    query = request.args.get('query', '')
    print("Received search query:", query)
    try:
        # Construct the SQL query to search in multiple columns
        sql_query = text("""
            SELECT * 
            FROM boats 
            WHERE name LIKE :query 
            OR type LIKE :query 
            OR owner_id LIKE :query 
            OR rental_price LIKE :query
        """)
        print("SQL Query:", sql_query, "Query parameter:", f'%{query}%')

        # Execute the SQL query with the search parameter
        boats = conn.execute(sql_query, {'query': f'%{query}%'}).fetchall()
        print("Boats found:", boats)

        # Pass the search results and query string to the template
        return render_template('boat_search.html', boats=boats, query=query)
    except Exception as e:
        error = str(e)
        print(error)
        # Handle errors here, if any
        return render_template('error.html', message='An error occurred during search'), 500



if __name__ == '__main__':
    app.run(debug=True)
