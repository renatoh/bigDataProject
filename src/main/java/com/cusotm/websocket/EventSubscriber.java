package com.cusotm.websocket;

import com.cusotm.websocket.dto.MessageDTO;
import org.springframework.beans.factory.DisposableBean;
import org.springframework.stereotype.Component;
import org.springframework.web.socket.TextMessage;

import javax.annotation.Resource;
import java.io.IOException;
import java.util.List;

@Component
class EventSubscriber implements DisposableBean, Runnable {


    @Resource
    private ElasticSearchService elasticSearchService;

    private Thread thread;
    private volatile boolean someCondition = true;

    EventSubscriber() {

        this.thread = new Thread(this);
        this.thread.start();
    }

    @Override
    public void run() {
        while (someCondition) {
            try {
                Thread.sleep(ElasticSearchService.timeWindowInS * 1000);
                writeMessageToAllClients();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }

    @Override
    public void destroy() {
        someCondition = false;
    }

    private void writeMessageToAllClients() {

        MyTextWebSocketHandler.sessions.forEach(webSocketSession -> {
            List<MessageDTO> logMessages = elasticSearchService.getLogMessages();

            for (MessageDTO logMessage : logMessages) {

                try {

                    System.out.println("writing message");
                    webSocketSession.sendMessage(new TextMessage(logMessage.message + "\n"));

                } catch (IOException e) {
                    e.printStackTrace();

                }
            }
        });
    }
}
             
