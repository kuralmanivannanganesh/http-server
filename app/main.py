import socket  # noqa: F401

SERVER = "localhost"
PORT = 4221
ADDR = (SERVER, PORT)
MSG_LENGTH = 1024


'''
An HTTP request is made up of three parts, each separated by a CRLF (\r\n):

Request line. 
Zero or more headers, each ending with a CRLF.
Optional request body.
'''
def send_res_message(conn, msg):
    data_len = len(msg)
    res = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {data_len}\r\n\r\n{msg}"
    conn.sendall(res.encode())


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # TODO: Uncomment the code below to pass the first stage
    #
    server_socket = socket.create_server(ADDR, reuse_port=True)
    conn, addr = server_socket.accept() # wait for client
    message = conn.recv(MSG_LENGTH).decode()
    print(f"[RAW MESSAGE] : {message}")
    message_split = message.split("\r\n")
    print(f"[SPLIT MESSAGE] : {message_split}")

    req_line = message_split[0]
    recource = req_line.split(" ")[1]
    print(recource)
    if recource == "/":
        conn.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
    elif recource.startswith("/echo"):
        print()
        data = recource.split("/")[2]
        send_res_message(conn=conn, msg=data)
        # data_len = len(data)
        # res = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {data_len}\r\n\r\n{data}"
        # conn.sendall(res.encode())
    elif recource.startswith("/user-agent"):
        for header in message_split:
            if header.startswith("User-Agent"):
                agent = header.split(":")[1].strip()
                send_res_message(conn=conn, msg=agent)
    else:
        conn.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")
    conn.close()


if __name__ == "__main__":
    main()
