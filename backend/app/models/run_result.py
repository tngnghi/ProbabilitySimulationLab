"""The RunResult Model (For Later: Week 8)
pythonclass RunResult(Base):
    __tablename__ = "run_results"
    
    run_id = Column(UUID, ForeignKey("runs.id"), primary_key=True)
    observed_lift = Column(Float, nullable=False)
    p_value = Column(Float, nullable=False)
    ci_low = Column(Float, nullable=True)
    ci_high = Column(Float, nullable=True)
    power_json = Column(JSON, nullable=True)
    charts_json = Column(JSON, nullable=True)
    summary_json = Column(JSON, nullable=True)
Key columns:

observed_lift: The actual difference you saw (e.g., 0.125 = 12.5% lift)
p_value: Statistical significance (e.g., 0.032)
ci_*: Confidence interval bounds (e.g., between 0.10 and 0.15)
*_json: Store complex data as JSON

power_json: {effect_grid: [...], power: [...]}
charts_json: Plotly-ready arrays for visualization

"""