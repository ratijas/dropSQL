"""

/stmt
    : /create_stmt
    | /drop_stmt
    | /insert_stmt
    | /update_stmt
    | /delete_stmt
    | /select_stmt
    ;

/create_stmt
    : "/create" "table" existence /table_name "(" /columns_def ")" /drop
    ;

/drop_stmt
    : "/drop" "table" existence /table_name /drop
    ;

/insert_stmt
    : "/insert" "into" /table_name "(" /columns_names ")" "values" values /drop
    ;

/update_stmt
    : "/update" /table_name "set" /assignments /where_clause /drop
    ;

/delete_stmt
    : "/delete" "from" /table_name /where_clause /drop
    ;

/select_stmt
    : "/select" /result_columns
         "from" /from_body
                /where_clause
                /drop
    ;

/result_columns
    :                     /result_column
    | /result_columns "," /result_column
    ;

/result_column
    : "*"
    | expr /alias
    ;

/alias
    : /* empty */
    | "/as" /identifier
    | /identifier
    ;

/from_body
    : /aliased_table /join_clauses
    ;

/aliased_table
    : /table_name /alias
    ;

/join_clauses
    : /* empty */
    | /join_clauses /join_clause
    ;

/join_clause
    : /cross_join
    | /inner_join
    ;

/cross_join
    : "," /aliased_table
    ;

/inner_join
    : "/join" /aliased_table "/on" expr
    ;

existence
    : /* empty */
    | "if" "not" "exists"
    ;

/table_name
    : /identifier
    ;

/columns_def
    :                   /column_def
    | /columns_def ","  /column_def
    ;

/column_def
    : /column_name type /primary_key
    ;

/columns_names
    :                    /column_name
    | /columns_names "," /column_name
    ;

/column_name
    : /identifier
    ;

type
    : "integer"
    | "float"
    | "varchar" "(" integer ")"
    ;

/primary_key
    : /* empty */
    | "/primary" "key"
    ;

values
    :            value
    | values "," value
    ;

value
    : "(" expressions ")"
    ;

expressions
    :                 expr
    | expressions "," expr
    ;

expr
    : literal
    | placeholder
    | /table_name /column_name
    |             /column_name
    | "(" expr ")"
    | expr binary_operator expr
    ;

/where_clause
    : /* empty */
    | "/where" expr
    ;

/assignments
    :                  /assignment
    | /assignments "," /assignment
    ;

/assignment
    : /column_name "=" expr
    ;

binary_operator
    : "*"
    | "/"
    | "+"
    | "-"
    | "<="
    | "<"
    | ">="
    | ">"
    | "="
    | "/="
    | "/and"
    | "/or"
    ;

literal
    : integer
    | float
    | text
    ;

placeholder
    : "?" integer
    ;

/drop
    : "/drop"
    ;

"""
