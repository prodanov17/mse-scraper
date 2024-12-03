package com.example.mseapi.dto;

import com.example.mseapi.model.StockData;
import lombok.Data;
import org.springframework.data.domain.Page;

@Data
public class StockDataDTO {
    private String companyKey;
    private String name;
    private Page<StockData> stockData;
}
