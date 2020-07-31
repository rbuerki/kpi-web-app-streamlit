import pytest
import pandas as pd
from src import plots  # noqa


def test_get_dimensions_for_plot():
    df = pd.DataFrame(
        {
            "kpi_name": ["Umsatz Total", "Umsatz Total", "Umsatz Inland"],
            "agg_level_value": ["e_1", "e_2", "e_1"],
            "agg_level_id": [1, 2, 2],
        }
    )
    (
        kpi_for_plots,
        entities_for_plots,
        agg_level_id_for_plots,
    ) = plots.get_dimensions_for_plot(df)
    assert kpi_for_plots == ["Umsatz Total", "Umsatz Inland"]
    assert entities_for_plots == ["e_1", "e_2"]
    assert entities_for_plots == ["e_1", "e_2"]
    assert agg_level_id_for_plots == [1, 2]


@pytest.mark.parametrize(
    "kpi, entities, expected",
    [
        (["kpi_1"], [1, 2, 3, 4, 5, 6, 7, 8, 9], False),
        (["kpi_1"], [1, 2, 3, 4, 5, 6, 7, 8], True),
        ([], [1, 2, 3, 4, 5, 6, 7, 8], False),
    ],
)
def test_check_if_plot(kpi, entities, expected):
    assert plots.check_if_plot(kpi, entities) == expected
