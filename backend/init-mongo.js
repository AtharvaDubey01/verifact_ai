// MongoDB Initialization Script for CrisisGuard AI

db = db.getSiblingDB('crisisguard');

// Create collections with validation schemas
db.createCollection('claims', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['claim_text', 'source', 'created_at'],
      properties: {
        claim_text: { bsonType: 'string' },
        source: { bsonType: 'string' },
        entities: { bsonType: 'array' },
        claim_type: { enum: ['health', 'politics', 'general', 'science', 'business'] },
        confidence: { bsonType: 'double', minimum: 0, maximum: 1 }
      }
    }
  }
});

// Create indexes for claims
db.claims.createIndex({ claim_text: 'text' });
db.claims.createIndex({ created_at: -1 });
db.claims.createIndex({ claim_type: 1 });
db.claims.createIndex({ 'embedding': 1 });

// Evidence collection
db.createCollection('evidence');
db.evidence.createIndex({ claim_id: 1 });
db.evidence.createIndex({ source_url: 1 });
db.evidence.createIndex({ reliability_score: -1 });

// Verdicts collection
db.createCollection('verdicts');
db.verdicts.createIndex({ claim_id: 1 });
db.verdicts.createIndex({ verdict: 1 });
db.verdicts.createIndex({ confidence: -1 });
db.verdicts.createIndex({ created_at: -1 });

// Clusters collection
db.createCollection('clusters');
db.clusters.createIndex({ cluster_id: 1 });
db.clusters.createIndex({ created_at: -1 });
db.clusters.createIndex({ is_trending: 1 });

// Sources collection
db.createCollection('sources');
db.sources.createIndex({ domain: 1 }, { unique: true });
db.sources.createIndex({ reliability_rating: -1 });

// Alerts collection
db.createCollection('alerts');
db.alerts.createIndex({ created_at: -1 });
db.alerts.createIndex({ severity: -1 });
db.alerts.createIndex({ is_active: 1 });

// Feedback collection
db.createCollection('feedback');
db.feedback.createIndex({ claim_id: 1 });
db.feedback.createIndex({ created_at: -1 });

// Users/Reviewers collection
db.createCollection('users');
db.users.createIndex({ email: 1 }, { unique: true });
db.users.createIndex({ role: 1 });

print('CrisisGuard AI database initialized successfully!');
