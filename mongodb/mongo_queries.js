// ==============================================================================
// AeroVision MongoDB Telemetry Ingestion, Indexing, and Aggregation Pipelines
// Database: aerovision_db | Collection: events
// ==============================================================================

// 1. Ingest Data via Terminal:
// mongoimport --db aerovision_db --collection events --type csv --headerline --file dataset/aerovision_events.csv

use aerovision_db;

// Verify total document count (Expected: 5,000)
db.events.countDocuments();

// 2. Index Creation for Performance Optimization
// Compound index on zone and severity for fast hazard filtering
db.events.createIndex({ zone: 1, severity: 1 });

// Single field indexes for query filters and sorting
db.events.createIndex({ mode: 1 });
db.events.createIndex({ event_type: 1 });
db.events.createIndex({ response_ms: -1 });

// 3. Aggregation Pipeline 1: Event Frequency by Type
// Quantifies distribution of sensory events across test sorties
db.events.aggregate([
  {
    $group: {
      _id: "$event_type",
      total: { $sum: 1 }
    }
  },
  {
    $sort: { total: -1 }
  }
]);

// 4. Aggregation Pipeline 2: Mean Response Latency by Operating Mode
// Benchmarks controller reaction times across navigation modes
db.events.aggregate([
  {
    $group: {
      _id: "$mode",
      avg_response_ms: { $avg: "$response_ms" },
      total_events: { $sum: 1 }
    }
  },
  {
    $sort: { avg_response_ms: -1 }
  }
]);

// 5. Aggregation Pipeline 3: Event Severity Distribution
// Categorizes incidents by severity level (Critical, High, Medium, Low)
db.events.aggregate([
  {
    $group: {
      _id: "$severity",
      total: { $sum: 1 }
    }
  },
  {
    $sort: { total: -1 }
  }
]);

// 6. Aggregation Pipeline 4: Safety Stop Latency Threshold Filtering
// Identifies safety stops where control latency exceeded the 130 ms safety boundary
db.events.aggregate([
  {
    $match: {
      event_type: "Safety Stop",
      response_ms: { $gt: 130 }
    }
  },
  {
    $count: "slow_stops"
  }
]);

// 7. Aggregation Pipeline 5: Zone-Wise Incident Breakdown
// Ranks physical zones by safety critical incident frequency
db.events.aggregate([
  {
    $match: {
      severity: { $in: ["High", "Critical"] }
    }
  },
  {
    $group: {
      _id: "$zone",
      high_severity_count: { $sum: 1 },
      avg_latency: { $avg: "$response_ms" }
    }
  },
  {
    $sort: { high_severity_count: -1 }
  }
]);

