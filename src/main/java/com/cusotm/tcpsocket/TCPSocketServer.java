package com.cusotm.tcpsocket;


import com.cusotm.websocket.ElasticSearchService;
import com.cusotm.websocket.dto.MessageDTO;

import java.io.*;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.List;
import java.util.stream.Collectors;

public class TCPSocketServer {
    private ServerSocket serverSocket;


    public void start(int port) throws IOException {
        serverSocket = new ServerSocket(port);
        while (true)
            new EchoClientHandler(serverSocket.accept()).start();
    }

    public void stop() throws IOException {
        serverSocket.close();
    }

    private static class EchoClientHandler extends Thread {
        private Socket clientSocket;
        private PrintWriter out;
        private BufferedReader in;

        private ElasticSearchService elasticSearchService = new ElasticSearchService();

        public EchoClientHandler(Socket socket) {
            this.clientSocket = socket;
        }

        public void run() {
            try {


                out = new PrintWriter(clientSocket.getOutputStream(), true);


                in = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
            } catch (IOException e) {
                e.printStackTrace();
            }

            try {

                List<MessageDTO> logMessages = elasticSearchService.getLogMessages();

                String messeagesString = logMessages.stream().map(m -> m.message).collect(Collectors.joining(","));
                out.println(messeagesString);

                in.close();
                out.close();
                clientSocket.close();

            } catch (Exception e) {

            }
        }
    }

    public static void main(String[] args) throws IOException {
        TCPSocketServer echoMultiServer = new TCPSocketServer();
        echoMultiServer.start(8080);
    }
}
