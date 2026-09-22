import pandas as pd
import matplotlib.pyplot as plt


BLUE = "#367BC1"
GREEN = "#039761"
WHITE ="#C9E0F7" 

# ============================================================
# Load experiment results
# ============================================================

results = pd.read_csv(
    "outputs/experiment_results.csv"
)

control = results[
    results["variant"] == "Control"
].iloc[0]

treatment = results[
    results["variant"] == "Treatment"
].iloc[0]

variants = [
    "Control",
    "Treatment"
]


# ============================================================
# Primary metric
# ============================================================

control_rate = (
    control["converting_clicks"]
    / control["eligible_clicks"]
)

treatment_rate = (
    treatment["converting_clicks"]
    / treatment["eligible_clicks"]
)

conversion_rates = [
    control_rate,
    treatment_rate
]

converted_clicks = [
    control["converting_clicks"],
    treatment["converting_clicks"]
]


# ============================================================
# 1. Conversion lift
# ============================================================

absolute_difference_pp = (
    treatment_rate - control_rate
) * 100

relative_lift_pct = (
    absolute_difference_pp
    / (control_rate * 100)
) * 100

fig, ax = plt.subplots(figsize=(4.2, 5))

x = [0, 1]
y = conversion_rates

ax.plot(
    x,
    y,
    marker="o",
    linewidth=2,
    color=BLUE
)

ax.set_xticks(x)
ax.set_xticklabels(
    variants,
    color=BLUE
)

ax.set_title(
    "Paid Booking Conversion Lift",
    color=BLUE
)

ax.set_ylabel(
    "Conversion Rate",
    color=BLUE
)

ax.set_ylim(
    0.005,
    0.0425
)

ax.yaxis.set_major_formatter(
    plt.FuncFormatter(
        lambda value, _: f"{value:.1%}"
    )
)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax.spines["left"].set_color(BLUE)
ax.spines["bottom"].set_color(BLUE)

ax.tick_params(
    axis="both",
    colors=BLUE
)

# Conversion rate labels
ax.text(
    x[0],
    y[0],
    f"{control_rate:.2%}",
    ha="center",
    va="bottom",
    color=BLUE
)

ax.text(
    x[1],
    y[1],
    f"{treatment_rate:.2%}",
    ha="center",
    va="bottom",
    color=BLUE
)

# Lift annotation
ax.annotate(
    f"+{absolute_difference_pp:.4f} pp\n"
    f"(+{relative_lift_pct:.2f}%)",
    xy=(0.5, (y[0] + y[1]) / 2),
    xytext=(0.5, 0.035),
    ha="center",
    color=GREEN
)

plt.tight_layout()

plt.savefig(
    "outputs/figures/conversion_lift.png",
    dpi=150
)

plt.close()


# ============================================================
# 2. Conversion rate and converted-click volume
# ============================================================

fig, axes = plt.subplots(
    1,
    2,
    figsize=(10, 5)
)


# ------------------------------------------------------------
# Conversion rate
# ------------------------------------------------------------

bars = axes[0].bar(
    variants,
    conversion_rates,
    color=BLUE
)

axes[0].set_title(
    "Conversion Rate",
    color=BLUE
)

axes[0].set_ylabel(
    "Conversion Rate",
    color=BLUE
)

axes[0].set_ylim(
    0,
    0.05
)

axes[0].yaxis.set_major_formatter(
    plt.FuncFormatter(
        lambda value, _: f"{value:.1%}"
    )
)


# ------------------------------------------------------------
# Converted clicks
# ------------------------------------------------------------

bars_clicks = axes[1].bar(
    variants,
    converted_clicks,
    color=BLUE
)

axes[1].set_title(
    "Converted Click Volume",
    color=BLUE
)

axes[1].set_ylabel(
    "Converting Clicks",
    color=BLUE
)

axes[1].set_ylim(
    0,
    max(converted_clicks) * 1.15
)


# ------------------------------------------------------------
# Shared styling
# ------------------------------------------------------------

for ax in axes:

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.spines["left"].set_color(BLUE)
    ax.spines["bottom"].set_color(BLUE)

    ax.tick_params(
        axis="both",
        colors=BLUE
    )


# Conversion rate labels
for bar, rate in zip(
    bars,
    conversion_rates
):
    axes[0].text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height(),
        f"{rate:.2%}",
        ha="center",
        va="bottom",
        color=BLUE
    )


# Converted click labels
for bar, clicks in zip(
    bars_clicks,
    converted_clicks
):
    axes[1].text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height(),
        f"{int(clicks):,}",
        ha="center",
        va="bottom",
        color=BLUE
    )


fig.suptitle(
    "Paid Booking Conversion: Rate and Volume",
    color=BLUE
)

plt.tight_layout()

plt.savefig(
    "outputs/figures/conversion_rate.png",
    dpi=150
)

plt.close()


# ============================================================
# 3. Business impact
# ============================================================

control_cpt = control[
    "cost_per_transaction"
]

treatment_cpt = treatment[
    "cost_per_transaction"
]

cost_per_transaction = [
    control_cpt,
    treatment_cpt
]

cost_difference = (
    treatment_cpt - control_cpt
)

fig, ax = plt.subplots(figsize=(7, 5))

bars = ax.bar(
    variants,
    cost_per_transaction,
    color=BLUE
)

ax.set_title(
    "Cost per Paid Transaction",
    color=BLUE
)

ax.set_ylabel(
    "Cost per Transaction",
    color=BLUE
)

ax.set_ylim(
    0,
    max(cost_per_transaction) * 1.15
)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax.spines["left"].set_color(BLUE)
ax.spines["bottom"].set_color(BLUE)

ax.tick_params(
    axis="both",
    colors=BLUE
)

for bar, value in zip(
    bars,
    cost_per_transaction
):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height(),
        f"{value:.2f}",
        ha="center",
        va="bottom",
        color=BLUE
    )

ax.text(
    0.8,
    max(cost_per_transaction) * 0.5,
    f"Difference: {cost_difference:.2f}",
    ma="left",
    color=WHITE
)

plt.tight_layout()

plt.savefig(
    "outputs/figures/business_impact.png",
    dpi=150
)

plt.close()


print("Figures saved:")
print("- outputs/figures/conversion_lift.png")
print("- outputs/figures/conversion_rate.png")
print("- outputs/figures/business_impact.png")