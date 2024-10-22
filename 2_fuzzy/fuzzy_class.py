from __future__ import annotations
from typing import List


class Fuzzy:
    def __init__(self, L: float, ml: float, mr: float, R: float):
        self.L = L
        self.ml = ml
        self.mr = mr
        self.R = R

    def add(self, other: Fuzzy) -> Fuzzy:
        return Fuzzy(
            L=self.L + other.L,
            ml=self.ml + other.ml,
            mr=self.mr + other.mr,
            R=self.R + other.R,
        )

    def substract(self, other: Fuzzy) -> Fuzzy:
        return Fuzzy(
            L=self.L - other.L,
            ml=self.ml - other.ml,
            mr=self.mr - other.mr,
            R=self.R - other.R,
        )

    def multiply_by(self, other: Fuzzy) -> Fuzzy:
        return Fuzzy(
            L=self.L * other.L,
            ml=self.ml * other.ml,
            mr=self.mr * other.mr,
            R=self.R * other.R,
        )

    def divide_by(self, other: Fuzzy) -> Fuzzy:
        return Fuzzy(
            L=self.L / other.R,
            ml=self.ml / other.mr,
            mr=self.mr / other.ml,
            R=self.R / other.L,
        )

    def reverse(self) -> Fuzzy():
        return Fuzzy(
            L=self.R,
            ml=self.mr,
            mr=self.ml,
            R=self.L,
        )

    def defuzzy(self) -> float:
        return (self.ml + self.mr) / 2

    def low_uncertainty(self) -> float:
        return self.defuzzy() - self.ml

    def high_uncertainty(self) -> float:
        return self.mr - self.defuzzy()

    def uncertainty_per(self) -> float:
        return (self.low_uncertainty() * 100) / self.defuzzy()

    def uncertainty_rel(self) -> float:
        return self.low_uncertainty() / self.defuzzy()

    def uncertainty_len(self) -> float:
        return self.mr - self.ml

    def plot(self, ax=None):
        points_x = [self.L, self.ml, self.mr, self.R]
        arbitrary_points_y = [0, 1, 1, 0]

        if ax is None:
            fig, ax = plt.subplots(1, 1, figsize=(6, 4))

        ax.plot(
            points_x,
            arbitrary_points_y,
            color="red",
            marker="o",
        )
        ax.set_ylabel("membership - μ(x)", color="red", fontsize=12)
        # ax2.set_ylabel('μ(x)', color='red',fontsize=14)
        ax.tick_params(axis="y", colors="red")

        return ax

    def __str__(self):
        return (
            "<"
            + str(self.L)
            + ", "
            + str(self.ml)
            + ", "
            + str(self.mr)
            + ", "
            + str(self.R)
            + ">"
        )


def plot_multiple(fuzzys: List[Fuzzy]):
    fig, ax = plt.subplots(1, 1, figsize=(6, 4))
    for fuzzy in fuzzys:
        ax2 = ax.twinx()
        ax2.set_label(fuzzy)
        fuzzy.plot(ax2)


def relative_fraction(total: Fuzzy, numerator: Fuzzy, denominator: Fuzzy):
    numerator_fixed = Fuzzy(
        numerator.defuzzy(),
        numerator.defuzzy(),
        numerator.defuzzy(),
        numerator.defuzzy(),
    )
    denominator_fixed = Fuzzy(
        denominator.defuzzy(),
        denominator.defuzzy(),
        denominator.defuzzy(),
        denominator.defuzzy(),
    )

    uncertainty_numerator = numerator.divide_by(denominator_fixed).high_uncertainty()
    uncertainty_denominator = numerator_fixed.divide_by(denominator).high_uncertainty()

    uncertainty_remaining = total.high_uncertainty() - (
        uncertainty_numerator + uncertainty_denominator
    )

    if uncertainty_numerator + uncertainty_denominator != total.high_uncertainty():
        print("NOK div")
        print(uncertainty_numerator + uncertainty_denominator)
        print(total.high_uncertainty())

    # Calculate shares of uncertainty
    share_a = (uncertainty_numerator / total.high_uncertainty()) * 100
    share_b = (uncertainty_denominator / total.high_uncertainty()) * 100
    remaining_share = 100 - (share_a + share_b)

    return round(remaining_share, 2), round(share_a, 2), round(share_b, 2)


def relative_addition(total: Fuzzy, first: Fuzzy, second: Fuzzy):
    first_relative = first.high_uncertainty()
    second_relative = second.high_uncertainty()

    if first_relative + second_relative != total.high_uncertainty():
        print("NOK add")
        print(first_relative + second_relative)
        print(total.high_uncertainty())

    # Calculate shares of uncertainty
    share_first = (first_relative / total.high_uncertainty()) * 100
    share_second = (second_relative / total.high_uncertainty()) * 100

    return round(share_first, 2), round(share_second, 2)


def relative_substraction(total: Fuzzy, first: Fuzzy, second: Fuzzy):
    first_relative = first.high_uncertainty()
    second_relative = second.high_uncertainty()

    if first_relative + second_relative != total.high_uncertainty():
        print("NOK sub")
        print(first_relative + second_relative)
        print(total.high_uncertainty())

    print("Comparison of relative sum vs total")
    print(total.high_uncertainty())
    print(first_relative - second_relative)

    # The value substracted hav 100% of th incertitude, the other reduce it

    # Calculate shares of uncertainty
    share_first = (first_relative / total.high_uncertainty()) * 100
    share_second = (second_relative / total.high_uncertainty()) * 100

    if share_second != 0:
        share_second = -round(share_second, 2)

    return 100, 0


def relative_multiplication(total: Fuzzy, A: Fuzzy, B: Fuzzy):
    A_fixed = Fuzzy(A.defuzzy(), A.defuzzy(), A.defuzzy(), A.defuzzy())
    B_fixed = Fuzzy(B.defuzzy(), B.defuzzy(), B.defuzzy(), B.defuzzy())

    uncertainty_a = A.multiply_by(B_fixed).high_uncertainty()
    uncertainty_b = B.multiply_by(A_fixed).high_uncertainty()

    uncertainty_remaining = total.high_uncertainty() - (uncertainty_a + uncertainty_b)

    if uncertainty_a + uncertainty_b != total.high_uncertainty():
        print("NOK mult")
        print(uncertainty_a + uncertainty_b)
        print(total.high_uncertainty())

    # Calculate shares of uncertainty
    share_a = (uncertainty_a / total.high_uncertainty()) * 100
    share_b = (uncertainty_b / total.high_uncertainty()) * 100
    remaining_share = 100 - (share_a + share_b)

    return round(share_a, 2), round(share_b, 2)
