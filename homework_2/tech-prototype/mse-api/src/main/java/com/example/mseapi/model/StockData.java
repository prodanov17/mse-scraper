package com.example.mseapi.model;

import com.fasterxml.jackson.annotation.JsonBackReference;
import jakarta.persistence.*;
import lombok.Data;
import lombok.ToString;

import java.time.LocalDate;

@Entity
@Data
public class StockData {
    //Date,Last trade price,Max,Min,Avg.,Price %chg.,Volume,Turnover in BEST in denars,Total turnover in denars
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne
    @JoinColumn(name = "company_key", nullable = false)
    @JsonBackReference
    @ToString.Exclude
    private Company company;

    private LocalDate date;

    private Double price;
    private Double averagePrice;
    private Double max;
    private Double min;
    private Double priceChange;
    private Double volume;
    private Double bestTurnover;
    private Double totalTurnover;

}
