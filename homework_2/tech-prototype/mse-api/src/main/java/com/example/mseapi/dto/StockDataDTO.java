package com.example.mseapi.dto;

import com.example.mseapi.model.StockData;
import lombok.Data;
import org.springframework.data.domain.Page;

@Data
public class StockDataDTO {
    private String short_name;
    private String name;
    private Double price;
    private Page<StockData> stockData;
}
