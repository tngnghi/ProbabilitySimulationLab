"""The Run Model (For Later: Week 6)
pythonclass Run(Base):
    __tablename__ = "runs"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    experiment_id = Column(UUID, ForeignKey("experiments.id"), nullable=False)
    method = Column(String, nullable=False)  # "ztest" or "permutation"
    n_sim = Column(Integer, default=20000)
    seed = Column(Integer, nullable=True)
    status = Column(String, default="queued")  # queued, running, success, failed
    progress = Column(Float, default=0.0)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
Key columns:

method: Which test you ran (z-test vs permutation)
status: Track progress (queued → running → success)
progress: 0.0 to 1.0 (0% to 100% done)
started_at, finished_at: Track timing

Why track these?

Frontend polls: "Is my run done yet?" (checks status)
Shows progress bar (checks progress)
If failed, shows error (error_message)

"""