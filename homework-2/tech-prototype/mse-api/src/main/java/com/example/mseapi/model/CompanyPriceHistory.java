package com.example.mseapi.model;

import jakarta.persistence.*;

import java.util.List;

@Entity
public class CompanyPriceHistory {
    //Date,Last trade price,Max,Min,Avg.,Price %chg.,Volume,Turnover in BEST in denars,Total turnover in denars
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne
    @JoinColumn(name = "company_id", nullable = false)
    private Company company;

}
