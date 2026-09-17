# Campaign Experiment Design

## 1. Business Context & Experiment Objective

### Business Context

The OTA marketing team uses paid search to acquire users who may eventually make hotel bookings.

Campaign performance is usually monitored through impressions, clicks, conversion rate, CAC, and ROAS. These metrics are useful for reporting, but they are descriptive. A campaign with a higher conversion rate is not necessarily causing more bookings, since results can also be affected by audience mix, timing, auction conditions, and other factors.

The marketing team therefore wants to test whether changing the campaign message affects downstream booking behavior.

### Experiment Objective

Test whether a new paid-search campaign message changes the rate at which eligible users make a confirmed hotel booking.

The intervention is limited to the campaign message. The main campaign conditions should remain consistent across variants, including:

* Target audience
* Destination
* Offer
* Landing experience
* Experiment period

### Experiment Question

> Does the treatment campaign message produce a different confirmed booking conversion rate than the existing campaign message among eligible users?

### Why an Experiment

Historical campaign data can show relationships between campaign characteristics and outcomes, but it cannot by itself establish causality.

A controlled experiment provides a defined comparison between two campaign conditions and allows the analysis to estimate the difference in booking outcomes under the experiment design.

---

## 2. Experiment Design

### Experiment Overview

The experiment compares the existing paid-search message with a new message for the same hotel campaign.

| Variant       | Campaign Message                                | Description               |
| ------------- | ----------------------------------------------- | ------------------------- |
| Control (A)   | “Bali Hotels — Up to 30% Off”                   | Existing campaign message |
| Treatment (B) | “Plan Your Bali Getaway — Hotels Up to 30% Off” | New campaign message      |

The treatment changes the messaging and positioning while keeping the destination and core offer consistent.

### Experimental Population

The population consists of users eligible for the paid-search campaign during the experiment period.

Eligibility is defined before assignment. Post-assignment actions such as clicks, OTA visits, or booking activity should not determine whether a user belongs to the experiment population.

### Experimental Unit

The primary unit of analysis is the **eligible user**.

Each eligible user is assigned to one experimental condition according to the experiment's allocation mechanism.

### Assignment

Target allocation is 50% Control and 50% Treatment.

Assignment should happen before post-assignment outcomes are observed and should not depend on expected booking behavior.

The primary analysis uses an **Intention-to-Treat (ITT)** framework. Users remain in their assigned group regardless of whether they later receive an impression, click, reach the OTA, or can be linked to a booking.

### Hypotheses

**Null hypothesis (H0)**

The confirmed booking conversion rate is the same for Control and Treatment.

**Alternative hypothesis (H1)**

The confirmed booking conversion rate differs between Control and Treatment.

The test is two-sided because the treatment could increase or decrease conversion.

### Primary Metric

**Confirmed booking conversion rate**

```text
Confirmed Booking Conversion Rate
=
Users with at least one confirmed booking
/
Eligible users assigned to the experiment
```

The metric is user-based. A user with multiple bookings is still counted once for the primary conversion metric.

### Secondary Metrics

The following metrics will help explain the campaign and booking funnel:

* Impression rate
* Click-through rate (CTR)
* OTA session rate
* Hotel-view rate
* Booking initiation rate
* Booking completion rate
* Confirmed booking rate
* Average booking value
* CAC
* ROAS

These are secondary measures and should not replace the primary experiment metric.

### Guardrails

The experiment will also monitor:

* Cancellation rate
* Confirmed booking value
* Average booking value
* Customer quality indicators

These help identify cases where a change in conversion is accompanied by changes in booking value or customer quality.

---

## 3. Measurement Architecture

### 3.1 Measurement Objective

The main measurement challenge is connecting the experiment condition in Google Ads to downstream OTA behavior and bookings.

The expected path is:

```text
Google Ads Experiment
        ↓
Experiment Arm
        ↓
Campaign / Ad / Click
        ↓
Click Identifier
        ↓
OTA Session
        ↓
Customer
        ↓
Booking
```

The project does not assume that every user can be traced through the full chain. Linkage gaps will be measured during validation.

### 3.2 Google Ads Experiment

The experiment is assumed to use Google Ads experiment functionality, with one arm representing the existing campaign configuration and the other containing the new campaign message.

The target traffic split is 50/50. Actual delivery may differ because of auction dynamics, bidding, ad quality, budget constraints, and other campaign factors.

For Search experiments, the split method can be cookie-based or search-based:

* **Cookie-based:** a user is assigned to one version and is designed to remain in that version.
* **Search-based:** assignment is randomized at the search level, so the same user may encounter both versions across searches.

The split method needs to be recorded because it affects how exposure and contamination are interpreted.

### 3.3 Google Ads Experiment Data

The experiment metadata should capture:

```text
experiment_id
experiment_name
experiment_arm
campaign_id
experiment_start_datetime
experiment_end_datetime
traffic_split
split_method
```

Google Ads experiment reporting provides aggregate performance by experiment arm, but it is not treated here as a customer-level assignment table.

A separate measurement path is therefore needed to connect advertising activity to OTA users and bookings.

### 3.4 Click-Level Measurement

Where available, a click identifier such as a GCLID can connect an advertising click to first-party tracking.

The click-level data should contain:

```text
gclid
campaign_id
ad_id
ad_group_id
click_timestamp
cost
```

The GCLID is a **linkage key**, not the experiment assignment itself.

Experiment assignment remains a separate concept derived from the experiment configuration and campaign/ad mapping.

### 3.5 OTA Tracking

When a user reaches the OTA, first-party tracking should retain the advertising identifier and associate it with the user's session.

```text
session_id
gclid
event_timestamp
event_type
```

Example events:

```text
landing
search
hotel_view
booking_start
booking_complete
```

The linkage is:

```text
Google Ads Click
       ↓
     GCLID
       ↓
  OTA Session
```

### 3.6 Customer Identity Resolution

A session may later be associated with a customer through login, account activity, booking activity, or another first-party identity mechanism.

```text
session_id
customer_id
identity_timestamp
```

The resulting path is:

```text
GCLID
  ↓
Session
  ↓
Customer
```

Identity resolution will not be assumed to be complete. Some sessions may remain anonymous or fail to resolve to a customer.

### 3.7 Booking Data

The booking system provides the downstream business outcome.

```text
booking_id
customer_id
booking_timestamp
booking_value
booking_status
cancellation_status
```

The full measurement path is:

```text
Experiment Arm
      ↓
Campaign / Ad
      ↓
GCLID
      ↓
Session
      ↓
Customer
      ↓
Booking
```

The primary analysis requires a defensible connection between experimental assignment and the customer's outcome.

### 3.8 Experiment Assignment vs Marketing Attribution

These are two different concepts:

**Experiment assignment**

> Which experimental condition was the user assigned to?

**Marketing attribution**

> Which marketing touchpoint receives credit for the booking?

```text
Experiment Assignment ≠ Marketing Attribution
```

The Control vs Treatment comparison should therefore be based on experimental assignment, not on whichever campaign receives attribution credit for a booking.

### 3.9 Expected Measurement Gaps

The synthetic data will include realistic gaps such as:

* Missing click identifiers
* Missing session identifiers
* Sessions that cannot be linked to a customer
* Multiple clicks from the same customer
* Multiple sessions from the same customer
* Multiple bookings from the same customer
* Delayed identity resolution
* Delayed conversions
* Cancelled bookings
* Cross-device activity that cannot be reliably linked
* Advertising activity that cannot be connected to first-party data
* Potential cross-variant exposure

These gaps will be measured rather than silently removed.

---

## 4. Data Requirements & Analytical Data Model

### 4.1 Data Sources

The experiment requires five logical data sources:

| Source                | Purpose                                       |
| --------------------- | --------------------------------------------- |
| Google Ads Experiment | Defines experiment arms and configuration     |
| Google Ads Clicks     | Captures advertising activity and cost        |
| OTA Tracking          | Connects clicks to sessions and funnel events |
| Customer Identity     | Connects sessions to customers                |
| Booking System        | Provides booking and economic outcomes        |

The sources are connected through available identifiers rather than assuming a single user ID exists across all systems.

### 4.2 Experiment Metadata

**Table: `experiment_metadata`**

| Field                       | Description                    |
| --------------------------- | ------------------------------ |
| `experiment_id`             | Unique experiment identifier   |
| `experiment_name`           | Experiment name                |
| `experiment_arm`            | Control or Treatment           |
| `campaign_id`               | Associated campaign identifier |
| `experiment_start_datetime` | Experiment start               |
| `experiment_end_datetime`   | Experiment end                 |
| `traffic_split`             | Target allocation              |
| `split_method`              | Cookie-based or search-based   |

This table defines the experiment configuration and the relationship between campaigns and experiment arms.

### 4.3 Google Ads Click Data

**Table: `ad_clicks`**

| Field             | Description                                |
| ----------------- | ------------------------------------------ |
| `gclid`           | Google click identifier                    |
| `campaign_id`     | Google Ads campaign identifier             |
| `ad_id`           | Advertisement identifier                   |
| `ad_group_id`     | Ad group identifier                        |
| `click_timestamp` | Time of click                              |
| `cost`            | Advertising cost associated with the click |

### 4.4 OTA Event Data

**Table: `ota_events`**

| Field             | Description                      |
| ----------------- | -------------------------------- |
| `session_id`      | OTA session identifier           |
| `gclid`           | Captured Google click identifier |
| `event_timestamp` | Event timestamp                  |
| `event_type`      | Type of user event               |

Example event types:

```text
landing
search
hotel_view
booking_start
booking_complete
```

### 4.5 Customer Identity Mapping

**Table: `session_customer_map`**

| Field                | Description                         |
| -------------------- | ----------------------------------- |
| `session_id`         | OTA session identifier              |
| `customer_id`        | First-party customer identifier     |
| `identity_timestamp` | Time at which identity was resolved |

### 4.6 Booking Data

**Table: `bookings`**

| Field                 | Description                   |
| --------------------- | ----------------------------- |
| `booking_id`          | Unique booking identifier     |
| `customer_id`         | Customer who made the booking |
| `booking_timestamp`   | Booking timestamp             |
| `booking_value`       | Booking value                 |
| `booking_status`      | Booking status                |
| `cancellation_status` | Cancellation status           |

### 4.7 Analytical Experiment Dataset

The final analytical dataset will have a grain of:

> **One row per eligible user in the experiment population.**

Conceptually:

```text
experiment_id
customer_id
assigned_variant
assignment_timestamp

first_gclid
first_session_id

impression_flag
click_flag
session_flag
hotel_view_flag
booking_start_flag
booking_complete_flag
confirmed_booking_flag

booking_value
cancelled_booking_flag
ad_cost
```

Not every field will be populated for every user. Missing values are expected when the measurement chain cannot be completed.

### 4.8 Assignment and Outcome Separation

Assignment information must remain separate from post-assignment outcomes.

**Assignment / pre-treatment**

```text
experiment_id
assigned_variant
assignment_timestamp
```

**Post-assignment outcomes**

```text
impression_flag
click_flag
session_flag
hotel_view_flag
booking_start_flag
booking_complete_flag
confirmed_booking_flag
booking_value
cancelled_booking_flag
```

Post-assignment behavior should not be used to redefine the experiment population or assignment.

### 4.9 Identifier Relationships

The expected relationship is:

```text
experiment_metadata
        │
        │ campaign_id
        ↓
    ad_clicks
        │
        │ gclid
        ↓
    ota_events
        │
        │ session_id
        ↓
session_customer_map
        │
        │ customer_id
        ↓
    bookings
```

These relationships are not one-to-one.

For example:

* One customer may generate multiple clicks.
* One customer may generate multiple sessions.
* One session may contain multiple events.
* One customer may make multiple bookings.
* Some clicks may not map to an OTA session.
* Some sessions may not map to a customer.
* Some customers may not make a booking.

### 4.10 Linkage Quality

The analysis will measure how much of the experiment population can be connected through the measurement chain.

Key metrics include:

```text
Click Linkage Rate
= clicks with valid OTA linkage / total clicks

Customer Linkage Rate
= sessions linked to customer / measurable sessions

Booking Linkage Rate
= bookings linked to experiment population / relevant bookings
```

These are measurement-coverage metrics, not campaign performance metrics.

### 4.11 Analytical Principle

The analytical dataset needs to preserve three separate layers:

1. Experimental assignment
2. Advertising exposure and interaction
3. Downstream customer and booking outcomes

This allows the same dataset to support the primary ITT analysis and the diagnostic analysis of the measurement funnel.

---

## 5. Experiment Validity & Measurement Risks

A 50/50 split alone does not make the experiment valid. Assignment, exposure, tracking, and outcome measurement all need to be checked.

### 5.1 Randomization Balance

Control and Treatment should be comparable on relevant pre-treatment characteristics.

Potential checks:

* Device type
* Geography
* New vs returning customer
* Historical engagement
* Pre-experiment activity
* Other available pre-treatment variables

These checks are used to identify unexpected differences between groups before treatment exposure.

### 5.2 Sample Ratio Mismatch

Observed assignment should be compared with the intended 50/50 allocation.

A meaningful deviation may indicate issues with experiment configuration, eligibility, traffic allocation, or data collection.

The analysis should distinguish between:

* Intended assignment ratio
* Observed assignment ratio
* Observed advertising exposure ratio

These do not necessarily match.

### 5.3 Exposure and Assignment

Assignment does not guarantee that a user receives an impression.

A user may:

```text
Be assigned
    ↓
Receive no impression
    ↓
Or receive an impression but not click
    ↓
Or click but not reach the OTA
    ↓
Or reach the OTA without a measurable session
```

The primary analysis will retain users based on assignment. Exposure and delivery will be analyzed separately.

### 5.4 Contamination

Contamination occurs when a user assigned to one condition is exposed to the other.

The risk depends partly on the experiment split method. For example, search-based splitting can allow the same user to encounter different versions across searches.

Where the data allows it, cross-variant exposure will be measured rather than assumed to be zero.

### 5.5 Tracking Gaps

The measurement chain can break at several points.

Example:

```text
Google Ads Click
       ↓
   GCLID missing
       ↓
No reliable OTA linkage
```

Or:

```text
OTA Session
       ↓
Customer identity unresolved
       ↓
Cannot confidently connect to booking
```

The size of these gaps and their potential effect on downstream analysis should be documented.

### 5.6 Multiple Sessions and Bookings

A customer may interact with the OTA multiple times and make multiple bookings.

The analysis therefore needs explicit rules for:

* Selecting the relevant experimental exposure
* Connecting sessions to customers
* Counting users in the primary metric
* Handling multiple bookings
* Calculating booking value

For the primary conversion metric, a user is considered converted if they have at least one qualifying confirmed booking within the defined outcome window.

### 5.7 Delayed Conversions

A user may be exposed during the experiment but book later.

The experiment therefore needs a predefined outcome window and enough time after the experiment to observe eligible conversions.

Bookings outside the defined window will not automatically be counted as experiment outcomes.

### 5.8 Cancellation and Booking Quality

A completed booking is not necessarily an economically realized booking.

Some bookings may later be cancelled. The primary metric will use the predefined confirmed-booking definition, while cancellation and booking value will be evaluated separately.

### 5.9 Campaign Configuration Changes

Changes during the experiment can affect interpretation.

Relevant changes include:

* Budget
* Bidding strategy
* Targeting
* Geographic coverage
* Offer
* Landing experience
* Campaign structure
* Experiment allocation

Material changes should be recorded during the experiment period.

### 5.10 Measurement Population vs Full Experiment Population

There are two populations to keep separate.

**Full experiment population**

```text
All eligible users assigned to Control or Treatment
```

**Linked measurement population**

```text
Users for whom advertising activity can be connected
to first-party sessions, customers, or bookings
```

The primary ITT analysis should preserve the full experiment population where assignment is observable.

Linkage restrictions should be analyzed separately rather than silently redefining the experiment population.

---

## 6. Key Design Decisions

The main decisions from Day 1 are:

| Decision             | Definition                               |
| -------------------- | ---------------------------------------- |
| Experimental unit    | Eligible user                            |
| Variants             | Existing message vs new message          |
| Target allocation    | 50/50                                    |
| Primary framework    | Intention-to-Treat (ITT)                 |
| Primary metric       | Confirmed booking conversion rate        |
| Secondary metrics    | Funnel, CAC, ROAS, booking value         |
| Guardrails           | Cancellation and booking quality         |
| Assignment basis     | Experimental assignment                  |
| Attribution basis    | Separate from experiment assignment      |
| Click linkage        | GCLID where available                    |
| Analytical grain     | One row per eligible user                |
| Measurement approach | Event-level data linked across systems   |
| Missing linkage      | Quantified rather than silently excluded |

The experiment is designed to answer a causal campaign question while keeping the measurement limitations visible. The synthetic data will therefore be built from event-level records rather than a precomputed A/B summary table.