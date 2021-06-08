# importing create_app(function)(variable) from the silverhorse(package)
# __init__.py file makes a directory as python package whcih can then be imported
from silverhorse import create_app

# making the app(variable) from the silverhorse(app)(pacakage)
app = create_app()

# setting enviroment variable
if __name__ == '__main__':
    app.run(debug=True)
