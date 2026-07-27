"""Add train management models.

Revision ID: a4d9e2c7b1f0
Revises: fb1884baccad
Create Date: 2026-07-24
"""

from alembic import op
import sqlalchemy as sa


revision = "a4d9e2c7b1f0"
down_revision = "fb1884baccad"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "trains",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("type", sa.Enum("PASSENGER", "EXPRESS", "FREIGHT", "HIGH_SPEED", name="traintype"), nullable=False),
        sa.Column("total_seat", sa.Integer(), nullable=False),
        sa.Column("available_seat", sa.Integer(), nullable=False),
        sa.Column("status", sa.Enum("ACTIVE", "INACTIVE", "MAINTENANCE", "DELAYED", name="trainstatus"), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "stations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("train_number", sa.String(10), nullable=False),
        sa.Column("city", sa.String(50), nullable=False),
        sa.Column("platform", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("train_number", name=op.f("uq_stations_train_number")),
    )
    op.create_table(
        "schedules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("train_id", sa.Integer(), nullable=False),
        sa.Column("from_station_id", sa.Integer(), nullable=False),
        sa.Column("to_station_id", sa.Integer(), nullable=False),
        sa.Column("departure_time", sa.Time(), nullable=False),
        sa.Column("arrival_time", sa.Time(), nullable=False),
        sa.Column("status", sa.Enum("SCHEDULED", "DELAYED", "CANCELLED", "COMPLETED", name="schedulestatus"), nullable=False),
        sa.Column("platform", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["train_id"], ["trains.id"], name=op.f("fk_schedules_train_id_trains")),
        sa.ForeignKeyConstraint(["from_station_id"], ["stations.id"], name=op.f("fk_schedules_from_station_id_stations")),
        sa.ForeignKeyConstraint(["to_station_id"], ["stations.id"], name=op.f("fk_schedules_to_station_id_stations")),
    )
    op.create_table(
        "bookings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("booking_ref", sa.Text(), nullable=False),
        sa.Column("passenger_name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(100), nullable=False),
        sa.Column("phone", sa.String(20), nullable=False),
        sa.Column("train_id", sa.Integer(), nullable=False),
        sa.Column("schedule_id", sa.Integer(), nullable=False),
        sa.Column("seat_number", sa.String(10), nullable=False),
        sa.Column("fare", sa.Numeric(10, 2), nullable=False),
        sa.Column("status", sa.Enum("PENDING", "CONFIRMED", "CANCELLED", "COMPLETED", name="bookingstatus"), nullable=False),
        sa.Column("from_station", sa.String(100), nullable=False),
        sa.Column("to_station", sa.String(100), nullable=False),
        sa.Column("departure_time", sa.Time(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["train_id"], ["trains.id"], name=op.f("fk_bookings_train_id_trains")),
        sa.ForeignKeyConstraint(["schedule_id"], ["schedules.id"], name=op.f("fk_bookings_schedule_id_schedules")),
        sa.UniqueConstraint("booking_ref", name=op.f("uq_bookings_booking_ref")),
        sa.UniqueConstraint("email", name=op.f("uq_bookings_email")),
    )
    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("booking_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("method", sa.Enum("CARD", "MPESA", "CASH", "BANK_TRANSFER", name="paymentmethod"), nullable=False),
        sa.Column("card_last4", sa.String(4)),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("transaction_id", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"], name=op.f("fk_payments_booking_id_bookings")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_payments_user_id_users")),
    )
    op.create_table(
        "user_favourites",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("train_id", sa.Integer(), nullable=False),
        sa.Column("station_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_user_favourites_user_id_users")),
        sa.ForeignKeyConstraint(["train_id"], ["trains.id"], name=op.f("fk_user_favourites_train_id_trains")),
        sa.ForeignKeyConstraint(["station_id"], ["stations.id"], name=op.f("fk_user_favourites_station_id_stations")),
        sa.PrimaryKeyConstraint("user_id", "train_id", "station_id", name=op.f("pk_user_favourites")),
    )


def downgrade():
    op.drop_table("user_favourites")
    op.drop_table("payments")
    op.drop_table("bookings")
    op.drop_table("schedules")
    op.drop_table("stations")
    op.drop_table("trains")
