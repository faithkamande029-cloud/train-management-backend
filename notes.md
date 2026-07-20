## Quering a Database
Querying a database means requesting specific data from a database using a structured set of rules or filters.

## Common Queries
- all() - Retrieves a list of all records matching a query
- filter() - A SQLAlchemy method that allows you to apply complex conditional filters. == > <
- filter_by() - A simpler SQLAlchemy method for filtering based on direct equality checks.
- first() - Retrieves the first record that matches a query, or None if no match.
make_response() - A Flask function that creates a customizable HTTP response.
- 404 Status Code - HTTP code meaning the requested resource was not found.
- JSON Response - Data returned from the server in structured JSON format.
- order_by() - Sorts the results. Default is ascending (A–Z).
- delete() - deletes one record 