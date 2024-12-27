package com.example.mseapi.service;

import com.example.mseapi.dto.NewsSentimentDTO;

public interface NewsService {
    NewsSentimentDTO getNewsSentiment(String key);
}
