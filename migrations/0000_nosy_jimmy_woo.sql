CREATE TABLE `agent_status` (
	`name` text PRIMARY KEY NOT NULL,
	`status` text NOT NULL,
	`last_scan` text NOT NULL,
	`signals_found` integer DEFAULT 0 NOT NULL
);
--> statement-breakpoint
CREATE TABLE `bot_state` (
	`key` text PRIMARY KEY NOT NULL,
	`value` text NOT NULL
);
--> statement-breakpoint
CREATE TABLE `open_positions` (
	`token_id` text PRIMARY KEY NOT NULL,
	`side` text NOT NULL,
	`size` real NOT NULL,
	`entry_price` real NOT NULL,
	`label` text NOT NULL,
	`opened_at` text NOT NULL
);
--> statement-breakpoint
CREATE TABLE `pending_approvals` (
	`id` text PRIMARY KEY NOT NULL,
	`label` text NOT NULL,
	`side` text NOT NULL,
	`size` real NOT NULL,
	`edge` real NOT NULL,
	`source` text NOT NULL,
	`score` integer NOT NULL,
	`market_prob` real NOT NULL,
	`model_prob` real NOT NULL,
	`timestamp` text NOT NULL,
	`status` text DEFAULT 'pending' NOT NULL
);
--> statement-breakpoint
CREATE TABLE `trades` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`token_id` text NOT NULL,
	`label` text NOT NULL,
	`exit_price` real NOT NULL,
	`pnl` real NOT NULL,
	`closed_at` text NOT NULL
);
