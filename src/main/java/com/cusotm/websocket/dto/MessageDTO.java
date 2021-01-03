package com.cusotm.websocket.dto;

public class MessageDTO {
    
    public String message;
    public String date;

    public MessageDTO(final String message, final String date) {
        this.message = message;
        this.date = date;
    }
}
