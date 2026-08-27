import argparse
import time
from pipeline.phase1_ingest import run_ingestion
from pipeline.phase2_vectorize import run_vectorization
from pipeline.utils import setup_logging

logger = setup_logging(__name__)

def main():
    parser = argparse.ArgumentParser(description="IP-SAKTI Sahayak Ingestion & Vectorization Pipeline")
    parser.add_argument("--phase", choices=["1", "2", "all"], required=True, 
                        help="Phase to run: 1 (Ingestion), 2 (Vectorization), or all")
                        
    args = parser.parse_args()
    
    start_total = time.time()
    
    if args.phase in ["1", "all"]:
        start_p1 = time.time()
        logger.info(">>> Launching Phase 1: Ingestion")
        run_ingestion()
        logger.info(f"<<< Phase 1 completed in {time.time() - start_p1:.2f} seconds")
        
    if args.phase in ["2", "all"]:
        start_p2 = time.time()
        logger.info(">>> Launching Phase 2: Vectorization")
        run_vectorization()
        logger.info(f"<<< Phase 2 completed in {time.time() - start_p2:.2f} seconds")
        
    logger.info(f"✨ Pipeline execution finished in {time.time() - start_total:.2f} seconds")

if __name__ == "__main__":
    main()
