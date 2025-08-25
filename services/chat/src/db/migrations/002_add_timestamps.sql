-- Add updated_at to all tables
ALTER TABLE dialogs ADD COLUMN updated_at TIMESTAMPTZ DEFAULT now();
ALTER TABLE messages ADD COLUMN updated_at TIMESTAMPTZ DEFAULT now();
ALTER TABLE attachments ADD COLUMN updated_at TIMESTAMPTZ DEFAULT now();
