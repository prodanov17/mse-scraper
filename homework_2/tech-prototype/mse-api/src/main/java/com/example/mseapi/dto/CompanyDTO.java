package com.example.mseapi.dto;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class CompanyDTO {
    private String name;
    private String shortName;
    private Double price;
    private Double priceChange;
}
