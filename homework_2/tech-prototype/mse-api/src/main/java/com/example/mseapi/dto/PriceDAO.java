package com.example.mseapi.dto;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class PriceDAO {
    private String company;
    private Double price;
    private Double priceChange;
}
