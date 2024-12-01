package com.example.mseapi.repository;

import com.example.mseapi.model.Company;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;


public interface CompanyRepository extends JpaRepository<Company, Long> {
}