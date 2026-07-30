

import click
from pandas import DataFrame

from core.configs import dataset_config
from core.exceptions import NotFitError
from data.loader import DataLoader
from data.pipeline import DataPipeline
from data.preprocessing import Splitter
from schemas.data import DatasetSplitSchema

from .base import BaseCommand


class DataCommand(BaseCommand):
    """Handle data pipeline operations."""

    def register(self, cli_group: click.Group) -> None:
        @cli_group.command()
        @click.option('--train', is_flag=True, help='Training and inverse transform only')
        @click.option('--predict', is_flag=True, help='Prediction only')
        @click.option('--full', is_flag=True, help='Full pipeline')
        def data(train: bool, predict: bool, full: bool) -> None:
            self.execute(
                train=train,
                predict=predict,
                full=full,
            )

    def execute(self, train: bool, predict: bool, full: bool) -> None:
        if full:
            self._run_full_pipeline()
        elif train:
            self._run_training()
        elif predict:
            self._run_prediction()
        else:
            click.echo("Usage: --train, --predict, --full, or --inverse")

    def _run_training(self) -> None:
        """Execute training only."""
        click.echo("Starting training...")
        pipeline = DataPipeline()
        train_set, test_set = pipeline.training()
        self._pipeline: DataPipeline = pipeline
        self._train_set: DatasetSplitSchema = train_set
        self._test_set: DatasetSplitSchema = test_set
        click.echo(f"✅ Train: {len(train_set.X)}, Test: {len(test_set.X)}")

        click.echo("Starting inverse transform...")
        if not hasattr(self, '_pipeline'):
            self._run_training()
        try:
            self._pipeline.inverse_predictor(self._train_set.y)
            click.echo("✅ Inverse transform successful")
        except NotFitError:
            click.echo("⚠️ Inverse transform skipped (numeric target)")

    def _run_prediction(self) -> None:
        """Execute prediction only."""
        click.echo("Starting prediction...")
        if not hasattr(self, '_pipeline'):
            self._run_training()

        df: DataFrame = DataLoader.from_file(dataset_config.filepath)
        feature, _ = Splitter.feature_target(df, load_target=False)
        pred_set: DatasetSplitSchema = self._pipeline.predictor(feature)
        self._pred_set: DatasetSplitSchema = pred_set
        click.echo(f"✅ Predict: {len(pred_set.X)}")

    def _run_full_pipeline(self) -> None:
        """Execute full pipeline."""
        click.echo("=" * 50)
        self._run_training()
        self._run_prediction()
        click.echo("Full pipeline completed")
        click.echo("=" * 50)
