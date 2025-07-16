-- Create IncidentEvidence table
CREATE TABLE IF NOT EXISTS "dashboard_incidentevidence" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "file" varchar(100) NOT NULL,
    "uploaded_at" datetime NOT NULL,
    "description" text NULL,
    "incident_report_id" integer NOT NULL REFERENCES "dashboard_incidentreport" ("id") DEFERRABLE INITIALLY DEFERRED,
    "uploaded_by_id" integer NULL REFERENCES "accounts_usuario" ("id") DEFERRABLE INITIALLY DEFERRED
);

-- Create IncidentHistory table
CREATE TABLE IF NOT EXISTS "dashboard_incidenthistory" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "action_type" varchar(20) NOT NULL,
    "description" text NOT NULL,
    "timestamp" datetime NOT NULL,
    "action_by_id" integer NULL REFERENCES "accounts_usuario" ("id") DEFERRABLE INITIALLY DEFERRED,
    "incident_id" integer NOT NULL REFERENCES "dashboard_incidentreport" ("id") DEFERRABLE INITIALLY DEFERRED
);

-- Create indexes
CREATE INDEX IF NOT EXISTS "dashboard_incidentevidence_incident_report_id" ON "dashboard_incidentevidence" ("incident_report_id");
CREATE INDEX IF NOT EXISTS "dashboard_incidentevidence_uploaded_by_id" ON "dashboard_incidentevidence" ("uploaded_by_id");
CREATE INDEX IF NOT EXISTS "dashboard_incidenthistory_action_by_id" ON "dashboard_incidenthistory" ("action_by_id");
CREATE INDEX IF NOT EXISTS "dashboard_incidenthistory_incident_id" ON "dashboard_incidenthistory" ("incident_id");
