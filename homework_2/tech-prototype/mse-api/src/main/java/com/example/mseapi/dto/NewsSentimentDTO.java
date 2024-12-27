package com.example.mseapi.dto;

import lombok.Data;

@Data
public class NewsSentimentDTO {
    private String key;
    private String sentiment;
    private Double score;
}
