from neo4j import GraphDatabase, basic_auth
from main_queries import delete_query, create_query, bought_query, contains_query, view_query, update_total_sum_query
import pprint
from pyvis.network import Network

print('1. Змоделювати предметну область онлайн-магазину.\n',
      '- Є: Items(id, name, price), Customers(id, name), Orders(id, date)\n',
      '- Customer може мати (bought) багато Orders\n',
      '- Item може входити (contains) в декілька Orders\n',
      '- Customer може переглядати (view), але при цьому не купувати Items.')

driver = GraphDatabase.driver(
  "neo4j+s://d770d583.databases.neo4j.io",
  auth=basic_auth("neo4j", "AwQZYHQunKb63kCUB0ojfopAqP-E8D7qZiUdWYehmO8"))

# Initializes the graph database
def create_data():
    with driver.session() as session:
        for query in delete_query:
            session.run(query)
        session.run(create_query)  

# Adds CONTAINS relationships between orders and items.
def add_contains_relationship(order_id, item_id):
    with driver.session() as session:
        session.run(contains_query, order_id=order_id, item_id=item_id)
        session.run(update_total_sum_query, order_id=order_id)

#  Adds BOUGHT relationships between customers and orders
def add_bought_relationship(customer_id, order_id):
    with driver.session() as session:
        session.run(bought_query, customer_id=customer_id, order_id=order_id)

# Adds VIEW relationships between customers and items
def add_view_relationship(customer_id, item_id):
    with driver.session() as session:
        session.run(view_query, customer_id=customer_id, item_id=item_id)


create_data()

add_contains_relationship(201514, 1)
add_contains_relationship(201514, 2)
add_contains_relationship(201515, 3)
add_contains_relationship(201516, 5)
add_contains_relationship(201516, 7)
add_contains_relationship(201516, 2)
add_contains_relationship(201517, 1)
add_contains_relationship(201518, 2)
add_contains_relationship(201518, 4)

add_bought_relationship(1, 201514)
add_bought_relationship(2, 201515)
add_bought_relationship(2, 201514)
add_bought_relationship(3, 201518)
add_bought_relationship(4, 201516)
add_bought_relationship(4, 201517)
add_bought_relationship(5, 201516)

add_view_relationship(1, 2)
add_view_relationship(1, 7)
add_view_relationship(3, 5)
add_view_relationship(3, 1)
add_view_relationship(3, 2)
add_view_relationship(6, 9)


print('2. Знайти Items які входять в конкретний Order (за Order id)')

def find_items_in_order(order_id):
    with driver.session() as session:
        result = session.run(
            """
            MATCH (o:Order {order_id: $order_id})-[:CONTAINS]->(i:Item)
            RETURN i
            """,
            order_id=order_id
        )
        items = [record["i"]._properties for record in result]
        return items

order_id = 201514
items_in_order = find_items_in_order(order_id)
pprint.pprint(items_in_order)


print('3. Підрахувати вартість конкретного Order')

def get_order_total(order_id):
    with driver.session() as session:
        result = session.run(
            """
            MATCH (o:Order {order_id: $order_id})
            RETURN o.total_sum AS total_cost
            """,
            order_id=order_id
        )
        total_cost = result.single()["total_cost"]
        return total_cost

order_id = 201514
total_cost = get_order_total(order_id)
print(f"Total cost of order {order_id}: ${total_cost}")


print('4. Знайти всі Orders конкретного Customer')

def find_orders_by_customer(customer_id):
    with driver.session() as session:
        result = session.run(
            """
            MATCH (c:Customer {customer_id: $customer_id})-[:BOUGHT]->(o:Order)
            RETURN o
            """,
            customer_id=customer_id
        )
        orders = [record["o"]._properties for record in result]
        return orders

customer_id = 4
orders = find_orders_by_customer(customer_id)
pprint.pprint(orders)


print('5. Знайти всі Items куплені конкретним Customer (через його Orders)')

def find_items_by_customer(customer_id):
    with driver.session() as session:
        result = session.run(
            """
            MATCH (c:Customer {customer_id: $customer_id})-[:BOUGHT]->(:Order)-[:CONTAINS]->(i:Item)
            RETURN i
            """,
            customer_id=customer_id
        )
        items = [record["i"]._properties for record in result]
        return items

customer_id = 4
items = find_items_by_customer(customer_id)
pprint.pprint(items)


print('6. Знайти загальну кількість Items куплені конкретним Customer (через його Order)')

def count_items_bought_by_customer(customer_id):
    with driver.session() as session:
        result = session.run(
            """
            MATCH (c:Customer {customer_id: $customer_id})-[:BOUGHT]->(:Order)-[:CONTAINS]->(i:Item)
            RETURN COUNT(i) AS total_items_bought
            """,
            customer_id=customer_id
        )
        total_items_bought = result.single()["total_items_bought"]
        return total_items_bought

customer_id = 4
total_items_bought = count_items_bought_by_customer(customer_id)
print("Total items bought by customer:", total_items_bought)


print('7. Знайти для Customer на яку загальну суму він придбав товарів (через його Order)')

def total_spent_by_customer(customer_id):
    with driver.session() as session:
        result = session.run(
            """
            MATCH (c:Customer {customer_id: $customer_id})-[:BOUGHT]->(o:Order)
            RETURN SUM(o.total_sum) AS total_spent_by_customer
            """,
            customer_id=customer_id
        )
        total_spent_by_customer = result.single()["total_spent_by_customer"]
        return total_spent_by_customer

customer_id = 4
total_spent = total_spent_by_customer(customer_id)
print("Total spent by customer:", total_spent)


print('8. Знайти скільки разів кожен товар був придбаний, відсортувати за цим значенням')

def count_purchases_per_item():
    with driver.session() as session:
        result = session.run(
            """
            MATCH (i:Item)<-[:CONTAINS]-(:Order)
            RETURN i, COUNT(*) AS purchases
            ORDER BY purchases DESC
            """
        )
        purchases_per_item = [(record["i"], record["purchases"]) for record in result]
        return purchases_per_item

purchases_per_item = count_purchases_per_item()
for item, purchases in purchases_per_item:
    print(f"Item {item['item_id']} was purchased {purchases} times")


print('9. Знайти всі Items переглянуті (view) конкретним Customer')

def find_viewed_items(customer_id):
    with driver.session() as session:
        result = session.run(
            """
            MATCH (c:Customer {customer_id: $customer_id})-[:VIEW]->(i:Item)
            RETURN i
            """,
            customer_id=customer_id
        )
        viewed_items = [record["i"]._properties for record in result]
        return viewed_items

customer_id = 1
viewed_items = find_viewed_items(customer_id)
pprint.pprint(viewed_items)


print('10. Знайти інші Items що купувались разом з конкретним Item (тобто всі Items що входять до Order-s разом з даними Item)')

def find_related_items(item_id):
    with driver.session() as session:
        result = session.run(
            """
            MATCH (i1:Item {item_id: $item_id})<-[:CONTAINS]-(o:Order)-[:CONTAINS]->(i2:Item)
            WHERE i1 <> i2
            RETURN DISTINCT i2
            """,
            item_id=item_id
        )
        items = [record["i2"]._properties for record in result]
        return items

item_id = 5
related_items = find_related_items(item_id)
pprint.pprint(related_items)


print('11. Знайти Customers які купили даний конкретний Item')

def find_customers_who_bought_item(item_id):
    with driver.session() as session:
        result = session.run(
            """
            MATCH (c:Customer)-[:BOUGHT]->(:Order)-[:CONTAINS]->(i:Item)
            WHERE i.item_id = $item_id
            RETURN DISTINCT c
            """,
            item_id=item_id
        )
        customers = [record["c"]._properties for record in result]
        return customers

item_id = 1
customers = find_customers_who_bought_item(item_id)
pprint.pprint(customers)


print('12. Знайти для певного Customer(а) товари, які він переглядав, але не купив')

def find_items_viewed_but_not_bought(customer_id):
    with driver.session() as session:
        result = session.run(
            """
            MATCH (c:Customer {customer_id: $customer_id})-[:VIEW]->(i:Item)
            WHERE NOT EXISTS {
                (c)-[:BOUGHT]->(:Order)-[:CONTAINS]->(i)
            }
            RETURN i
            """,
            customer_id=customer_id
        )
        items = [record["i"]._properties for record in result]
        return items

customer_id = 1
items = find_items_viewed_but_not_bought(customer_id)
pprint.pprint(items)
