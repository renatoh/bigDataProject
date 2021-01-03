package com.cusotm.websocket.dto;


import com.fasterxml.jackson.annotation.JsonProperty;

public class Range{
    @JsonProperty("event.ingested") 
    public EventIngested eventIngested;
}

