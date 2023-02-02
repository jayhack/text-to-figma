mod_prompt = """# Data Schema:
actor(actor_id, first_name, last_name)
film(film_id, title, description, release_year, special_features, rating)
film_actor(actor_id: actor.actor_id, film_id: film.film_id)
film_category(film_id: film.film_id, category_id: category.category_id)
city(city_id, city)
category(category_id, name)
address(address_id, address, district, city_id: city.city_id, postal_code, phone)
customer(customer_id, first_name, last_name, email, address_id: address.address_id, create_date)
rental(rental_id, inventory_id: inventory.id, customer_id: customer.customer_id, return_date, rental_date)
inventory(inventory_id, film_id: film.film_id, store_id)

---

Query: Create an app that shows me all of the films and all of the actors, side-by-side

```
Title: Films and Actors Dashboard
Queries:
    Films: "SELECT * FROM film"
    Actors: "SELECT * FROM actors"
Components:
    FilmsTable:
        type: Table
        data: "{{queries.Films.data}}"
        columns: film_id, title, description, release_year
        layouts: # top left
            top: 80
            left: 2
            width: 20
            height: 500
    ActorsTable:
        type: Table
        data: "{{queries.Actors.data}}"
        columns: actor_id, first_name, last_name
        layouts: # top right
            top: 80
            left: 50
            width: 20
            height: 500
```

Modification: Order the films by date descending

```
Title: Films and Actors Dashboard
Queries:
    Films: "SELECT * FROM film ORDER BY release_year DESC"
    Actors: "SELECT * FROM actors"
Components:
    FilmsTable:
        type: Table
        data: "{{queries.Films.data}}"
        columns: film_id, title, description, release_year
        layouts: # top left
            top: 80
            left: 2
            width: 20
            height: 500
    ActorsTable:
        type: Table
        data: "{{queries.Actors.data}}"
        columns: actor_id, first_name, last_name
        layouts: # top right
            top: 80
            left: 50
            width: 20
            height: 500
```
---

Query: Create an app that shows me all of the films and their inventories, then when I select a film, it shows me all of the customers who have rented the film, ordered by date. It also gives me a form where I can select a customer by email and create a new rental for the currently selected film.

```
Title: Film Rentals Dashboard
Queries:
    Films: "SELECT film.*, inventory.inventory_id FROM film INNER JOIN inventory on inventory.film_id = film.film_id"
    FilmCustomers: "SELECT rental.rental_date, customer.* FROM customer INNER JOIN rental ON rental.customer_id = customer.customer_id INNER JOIN inventory ON inventory.inventory_id = rental.inventory_id WHERE inventory.film_id = {{components.FilmsTable.selectedRow.film_id}} ORDER BY rental.rental_date DESC"
    AllCustomers: "SELECT * FROM customer"
    CreateRental: "INSERT INTO rental (rental_date, customer_id, inventory_id) VALUES (CURRENT_DATE, {{components.CustomerSelect.value}}, {{components.FilmsTable.selectedRow.inventory_id}}"
Components:
    FilmsTable: 
        type: Table
        data: "{{queries.Films.data}}"
        columns: film_id, title, description, release_year, inventory_id
        onRowClicked: FilmCustomers
        layouts: # top left
            top: 80
            left: 2
            width: 20
            height: 500
    CustomersTable: 
        type: Table
        data: "{{queries.FilmCustomers.data}}"
        columns: customer_id, first_name, last_name, email
        layouts: # top right
            top: 80
            left: 50
            width: 20
            height: 500
    CustomerSelect:
        type: DropDown
        values: "{{queries.AllCustomers.data.map(x => x.customer_id)}}"
        display_values: "{{queries.AllCustomers.data.map(x => x.email)}}"
        placeholder: "Select Customer"
        layouts: # bottom left
            top: 580 
            left: 2
            width: 20
            height: 50
    CreateRentalSubmitButton:
        type: Button
        label: "submit"
        onClick: CreateRental
        layouts: # bottom right
            top: 580 
            left: 50
            width: 20
            height: 50
```

Modification: Add a button that, when I click it, it will create a new rental for the currently selected customer and the film with ID 27

```
Title: Film Rentals Dashboard
Queries:
    Films: "SELECT film.*, inventory.inventory_id FROM film INNER JOIN inventory on inventory.film_id = film.film_id"
    FilmCustomers: "SELECT rental.rental_date, customer.* FROM customer INNER JOIN rental ON rental.customer_id = customer.customer_id INNER JOIN inventory ON inventory.inventory_id = rental.inventory_id WHERE inventory.film_id = {{components.FilmsTable.selectedRow.film_id}} ORDER BY rental.rental_date DESC"
    AllCustomers: "SELECT * FROM customer"
    CreateRental: "INSERT INTO rental (rental_date, customer_id, inventory_id) VALUES (CURRENT_DATE, {{components.CustomerSelect.value}}, {{components.FilmsTable.selectedRow.inventory_id}}"
    CreateRental2: "INSERT INTO rental (rental_date, customer_id, inventory_id) VALUES (CURRENT_DATE, {{components.CustomerSelect.value}}, 27)"
Components:
    FilmsTable: 
        type: Table
        data: "{{queries.Films.data}}"
        columns: film_id, title, description, release_year, inventory_id
        onRowClicked: FilmCustomers
        layouts: # top left
            top: 80
            left: 2
            width: 20
            height: 500
    CustomersTable: 
        type: Table
        data: "{{queries.FilmCustomers.data}}"
        columns: customer_id, first_name, last_name, email
        layouts: # top right
            top: 80 
            left: 50
            width: 20
            height: 500
    CustomerSelect:
        type: DropDown
        values: "{{queries.AllCustomers.data.map(x => x.customer_id)}}"
        display_values: "{{queries.AllCustomers.data.map(x => x.email)}}"
        placeholder: "Select Customer"
        layouts: # bottom left
            top: 580 
            left: 2
            width: 20
            height: 50
    CreateRentalSubmitButton:
        type: Button
        label: "submit"
        onClick: CreateRental
        layouts: # bottom right
            top: 580 
            left: 50
            width: 20
            height: 50
    CreateRentalSubmitButton2:
        type: Button
        label: "submit"
        onClick: CreateRental2
        layouts: # below bottom right
            top: 620
            left: 50
            width: 20
            height: 50
```
---

Query: ...

```
Title: Recent Rentals Dashboard
Queries:
    Films: "SELECT film.name, rental.rental_date from film INNER JOIN inventory on inventory.film_id = film.film_id INNER JOIN rental ON inventory.inventory_id = rental.inventory_id ORDER BY rental.rental_date DESC"
Components:
    FilmsTable:
        type: Table
        data: "{{queries.Films.data}}"
        columns: name, rental_date
        layouts: # top left
            top: 80
            left: 2
            width: 20
            height: 500
```

Modification: Add a dropdown that allows me to select a customer, and then only show me the rentals for that customer
```
Title: Recent Rentals Dashboard
Queries:
    Films: "SELECT film.name, rental.rental_date from film INNER JOIN inventory on inventory.film_id = film.film_id INNER JOIN rental ON inventory.inventory_id = rental.inventory_id ORDER BY rental.rental_date DESC WHERE rental.customer_id = {{components.CustomerSelect.value}}"
    Customers: "SELECT * FROM customer"
Components:
    FilmsTable:
        type: Table
        data: "{{queries.Films.data}}"
        columns: name, rental_date
        layouts: # top left
            top: 80
            left: 2
            width: 20
            height: 500
    CustomerSelect:
        type: DropDown
        values: "{{queries.Customers.data.map(x => x.customer_id)}}"
        display_values: "{{queries.Customers.data.map(x => x.email)}}"
        placeholder: "Select Customer"
        onSelect: CityFilmRentals
        layouts: # bottom left
            top: 580
            left: 2
            width: 20
            height: 50
```

"""

def format_modification(original_prompt, gpt3_output, modification):
    return mod_prompt + f'Query: ... \n```{gpt3_output}```' + f'\n\nModification: {modification}\n```'