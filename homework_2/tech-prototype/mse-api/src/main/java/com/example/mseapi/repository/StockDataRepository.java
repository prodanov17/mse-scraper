package com.example.mseapi.repository;

import com.example.mseapi.dto.PriceDAO;
import com.example.mseapi.model.StockData;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

public interface StockDataRepository extends JpaRepository<StockData, Long> {
    Page<StockData> findByCompanyCompanyKeyAndDateBetween(
            String companyKey,
            LocalDate startDate,
            LocalDate endDate,
            Pageable pageable
    );
    @Query(value = """
    SELECT s.company_key, s.price, s.price_change
    FROM stock_data s
    INNER JOIN (
        SELECT company_key, MAX(date) AS latest_date
        FROM stock_data
        GROUP BY company_key
    ) latest
    ON s.company_key = latest.company_key AND s.date = latest.latest_date
""", nativeQuery = true)
    List<Object[]> findLatestStockDataForAllCompanies();

    @Query(value = """
    SELECT s.company_key, 
           COALESCE(s.price, 0.0) AS price, 
           COALESCE(s.price_change, 0.0) AS price_change
    FROM stock_data s
    INNER JOIN (
        SELECT company_key, MAX(date) AS latest_date
        FROM stock_data
        GROUP BY company_key
    ) latest
    ON s.company_key = latest.company_key AND s.date = latest.latest_date
    WHERE s.company_key = :companyKey
""", nativeQuery = true)
    Object[] findLatestStockDataForCompany(@Param("companyKey") String companyKey);


}
