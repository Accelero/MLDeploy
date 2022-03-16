# main function and entry point for the modelserver

import restapi

def main():
    #start flask server
    restapi.app.run(host='0.0.0.0', port=9000, debug=True)

if __name__ == '__main__':
    main()