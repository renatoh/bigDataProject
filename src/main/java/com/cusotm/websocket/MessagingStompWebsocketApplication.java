package com.cusotm.websocket;

import org.springframework.boot.SpringApplication;

import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.web.socket.TextMessage;

import java.io.IOException;


@SpringBootApplication
@EnableAsync
public class MessagingStompWebsocketApplication {


    public static void main(String[] args) {
        SpringApplication.run(MessagingStompWebsocketApplication.class, args);
    }


}
