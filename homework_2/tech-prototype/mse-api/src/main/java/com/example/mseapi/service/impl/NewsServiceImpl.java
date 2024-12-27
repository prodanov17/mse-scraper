package com.example.mseapi.service.impl;

import com.example.mseapi.dto.NewsSentimentDTO;
import com.example.mseapi.service.NewsService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Service
public class NewsServiceImpl implements NewsService {

    private static final String FLASK_API_URL = "http://localhost:5003/news/{key}/sentiment";

    @Autowired
    private RestTemplate restTemplate;

    @Override
    @Cacheable("newsSentiment")
    public NewsSentimentDTO getNewsSentiment(String key) {
            // Make a GET request to the Flask API to get news sentiment analysis
            ResponseEntity<NewsSentimentDTO> response = restTemplate.getForEntity(FLASK_API_URL, NewsSentimentDTO.class, key.toUpperCase());
            if (response.getStatusCode().is2xxSuccessful()) {
                return response.getBody();
            } else {
                // Log the error or return a default error response
                throw new RuntimeException("Failed to fetch news sentiment for symbol: " + key);
            }
    }
}