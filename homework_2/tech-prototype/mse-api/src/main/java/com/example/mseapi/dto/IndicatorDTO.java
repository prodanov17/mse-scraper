package com.example.mseapi.dto;

import lombok.Data;

@Data
public class IndicatorDTO {
    private String short_name;
    private String date;
    private Double close;
    private Double min;
    private Double max;
    private Double volume;
    private String indicator;
    private String signal;
}
