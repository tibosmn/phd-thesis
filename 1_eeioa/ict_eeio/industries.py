# From https://unstats.un.org/unsd/statcom/doc02/isic.pdf

isic_divisions = {}

#########################################
# A - Agriculture, hunting and forestry #
#########################################

# Agriculture, hunting and related service activities
div_01 = [
    "Animal products nec",
    "Cattle farming",
    "Cultivation of cereal grains nec",
    "Cultivation of crops nec",
    "Cultivation of oil seeds",
    "Cultivation of paddy rice",
    "Cultivation of plant-based fibers",
    "Cultivation of sugar cane, sugar beet",
    "Cultivation of vegetables, fruit, nuts",
    "Cultivation of wheat",
    "Meat animals nec",  # Farming of animals
    "Pigs farming",  # Farming of animals
    "Poultry farming",  # Farming of animals
    "Raw milk",  # Farming of animals
    "Wool, silk-worm cocoons",  # Farming of animals
    "Manure treatment (conventional), storage and land application",  # May go to Div 90
    "Manure treatment (biogas), storage and land application",  # May go to Div 90
]
isic_divisions["Agriculture, hunting and related service activities"] = div_01

# Forestry, logging and related service activities
div_02 = [
    "Forestry, logging and related service activities (02)",
]
isic_divisions["Forestry, logging and related service activities"] = div_02

###############
# B - Fishing #
###############

# Fishing, operation of fish hatcheries and fish farms; service activities incidental to fishing
div_05 = [
    "Fishing, operating of fish hatcheries and fish farms; service activities incidental to fishing (05)",
]
isic_divisions[
    "Fishing, operating of fish hatcheries and fish farms; service activities incidental to fishing (05)"
] = div_05

############################
# C - Mining and quarrying #
############################

# Mining of coal and lignite; extraction of peat
div_10 = [
    "Mining of coal and lignite; extraction of peat (10)",
]
isic_divisions["Mining of coal and lignite; extraction of peat"] = div_10

div_11 = [  # Extraction of crude petroleum and natural gas; service activities incidental to oil and gas extraction, excluding surveying
    "Extraction of crude petroleum and services related to crude oil extraction, excluding surveying",
    "Extraction of natural gas and services related to natural gas extraction, excluding surveying",
    "Extraction, liquefaction, and regasification of other petroleum and gaseous materials",  # Not explicit in ISIC
]
isic_divisions[
    "Extraction of crude petroleum and natural gas; service activities incidental to oil and gas extraction, excluding surveying"
] = div_11

# Mining of uranium and thorium ores
div_12 = [
    "Mining of uranium and thorium ores (12)",
]
isic_divisions["Mining of uranium and thorium ores"] = div_12

# Mining of metal ores
div_13 = [
    "Mining of iron ores",
    "Mining of precious metal ores and concentrates",
    "Mining of aluminium ores and concentrates",  # Non-ferrous metal ore
    "Mining of copper ores and concentrates",  # Non-ferrous metal ore
    "Mining of lead, zinc and tin ores and concentrates",  # Non-ferrous metal ore
    "Mining of nickel ores and concentrates",  # Non-ferrous metal ore
    "Mining of other non-ferrous metal ores and concentrates",  # Non-ferrous metal ore
]
isic_divisions["Mining of metal ores"] = div_13

# Other mining and quarrying
div_14 = [
    "Mining of chemical and fertilizer minerals, production of salt, other mining and quarrying n.e.c.",
    "Quarrying of sand and clay",
    "Quarrying of stone",
]
isic_divisions["Other mining and quarrying"] = div_14

#####################
# D - Manufacturing #
#####################

# Manufacture of food products and beverages
div_15 = [
    "Manufacture of beverages",
    "Manufacture of fish products",
    "Production of meat products nec",
    "Processing of Food products nec",
    "Processing of dairy products",
    "Processing of meat cattle",
    "Processing of meat pigs",
    "Processing of meat poultry",
    "Processing vegetable oils and fats",
    "Sugar refining",
    "Processed rice",  # Not explicit in ISIC
]
isic_divisions["Manufacture of food products and beverages"] = div_15

# Manufacture of tobacco products
div_16 = [
    "Manufacture of tobacco products (16)",
]
isic_divisions["Manufacture of tobacco products"] = div_16

# Manufacture of textiles
div_17 = [
    "Manufacture of textiles (17)",
]
isic_divisions["Manufacture of textiles"] = div_17

# Manufacture of wearing apparel; dressing and dyeing of fur
div_18 = [
    "Manufacture of wearing apparel; dressing and dyeing of fur (18)",
]
isic_divisions["Manufacture of wearing apparel; dressing and dyeing of fur"] = div_18

# Tanning and dressing of leather; manufacture of luggage, handbags, saddlery, harness and footwear
div_19 = [
    "Tanning and dressing of leather; manufacture of luggage, handbags, saddlery, harness and footwear (19)",
]
isic_divisions[
    "Tanning and dressing of leather; manufacture of luggage, handbags, saddlery, harness and footwear"
] = div_19

# Manufacture of wood and of products of wood and cork, except furniture; manufacture of articles of straw and plaiting materials
div_20 = [
    "Manufacture of wood and of products of wood and cork, except furniture; manufacture of articles of straw and plaiting materials (20)",
]
isic_divisions[
    "Manufacture of wood and of products of wood and cork, except furniture; manufacture of articles of straw and plaiting materials"
] = div_20

# Manufacture of paper and paper products
div_21 = [
    "Paper",
    "Pulp",
]
isic_divisions["Manufacture of paper and paper products"] = div_21

# Publishing, printing and reproduction of recorded media
div_22 = [
    "Publishing, printing and reproduction of recorded media (22)",
]
isic_divisions["Publishing, printing and reproduction of recorded media"] = div_22

# Manufacture of coke, refined petroleum products and nuclear fuel
div_23 = [
    "Manufacture of coke oven products",
    "Petroleum Refinery",
    "Processing of nuclear fuel",
]
isic_divisions["Manufacture of coke, refined petroleum products and nuclear fuel"] = (
    div_23
)

# Manufacture of chemicals and chemical products
div_24 = [
    "Chemicals nec",
    "Composting of food waste, incl. land application",  # Manufacture of fertilizers and nitrogen compounds
    "Composting of paper and wood, incl. land application",  # Manufacture of fertilizers and nitrogen compounds
    "N-fertiliser",
    "P- and other fertiliser",
]
isic_divisions["Manufacture of chemicals and chemical products"] = div_24

# Manufacture of rubber and plastics products
div_25 = [
    "Manufacture of rubber and plastic products (25)",
    "Plastics, basic",
]
isic_divisions["Manufacture of rubber and plastics products"] = div_25

# Manufacture of other non-metallic mineral products
div_26 = [
    "Manufacture of other non-metallic mineral products n.e.c.",
    "Manufacture of bricks, tiles and construction products, in baked clay",
    "Manufacture of cement, lime and plaster",
    "Manufacture of ceramic goods",
    "Manufacture of glass and glass products",
]
isic_divisions["Manufacture of other non-metallic mineral products"] = div_26

# Manufacture of basic metals
div_27 = [
    "Manufacture of basic iron and steel and of ferro-alloys and first products thereof",
    "Precious metals production",
    "Aluminium production",
    "Lead, zinc and tin production",
    "Copper production",
    "Other non-ferrous metal production",
    "Casting of metals",
]
isic_divisions["Manufacture of basic metals"] = div_27

# Manufacture of fabricated metal products, except machinery and equipment
div_28 = [
    "Manufacture of fabricated metal products, except machinery and equipment (28)",
]
isic_divisions[
    "Manufacture of fabricated metal products, except machinery and equipment"
] = div_28

# Manufacture of machinery and equipment n.e.c.
div_29 = [
    "Manufacture of machinery and equipment n.e.c. (29)",
]
isic_divisions["Manufacture of machinery and equipment n.e.c."] = div_29

# Manufacture of electrical machinery and apparatus n.e.c.
div_31 = ["Manufacture of electrical machinery and apparatus n.e.c. (31)"]
isic_divisions["Manufacture of electrical machinery and apparatus n.e.c."] = div_31

# Manufacture of medical, precision and optical instruments, watches and clocks
div_33 = [
    "Manufacture of medical, precision and optical instruments, watches and clocks (33)"
]
isic_divisions[
    "Manufacture of medical, precision and optical instruments, watches and clocks"
] = div_33

# Manufacture of motor vehicles, trailers and semi-trailers
div_34 = [
    "Manufacture of motor vehicles, trailers and semi-trailers (34)",
]
isic_divisions["Manufacture of motor vehicles, trailers and semi-trailers"] = div_34

# Manufacture of other transport equipment
div_35 = [
    "Manufacture of other transport equipment (35)",
]
isic_divisions["Manufacture of other transport equipment"] = div_35

# Manufacture of furniture; manufacturing n.e.c.
div_36 = [
    "Manufacture of furniture; manufacturing n.e.c. (36)",
]
isic_divisions["Manufacture of furniture; manufacturing n.e.c."] = div_36

# Recycling
div_37 = [
    "Re-processing of ash into clinker",
    "Re-processing of secondary aluminium into new aluminium",
    "Re-processing of secondary construction material into aggregates",
    "Re-processing of secondary copper into new copper",
    "Re-processing of secondary glass into new glass",
    "Re-processing of secondary lead into new lead, zinc and tin",
    "Re-processing of secondary other non-ferrous metals into new other non-ferrous metals",
    "Re-processing of secondary paper into new pulp",
    "Re-processing of secondary plastic into new plastic",
    "Re-processing of secondary preciuos metals into new preciuos metals",
    "Re-processing of secondary steel into new steel",
    "Re-processing of secondary wood material into new wood material",
    "Recycling of waste and scrap",
]
isic_divisions["Recycling"] = div_37


#########################################
# E - Electricity, gas and water supply #
#########################################

# Electricity, gas, steam and hot water supply
div_40 = [
    "Distribution and trade of electricity",
    "Production of electricity by Geothermal",
    "Production of electricity by biomass and waste",
    "Production of electricity by coal",
    "Production of electricity by gas",
    "Production of electricity by hydro",
    "Production of electricity by nuclear",
    "Production of electricity by petroleum and other oil derivatives",
    "Production of electricity by solar photovoltaic",
    "Production of electricity by solar thermal",
    "Production of electricity by tide, wave, ocean",
    "Production of electricity by wind",
    "Production of electricity nec",
    "Steam and hot water supply",
    "Transmission of electricity",
    "Manufacture of gas; distribution of gaseous fuels through mains",
]
isic_divisions["Electricity, gas, steam and hot water supply"] = div_40

# Collection, purification and distribution of water
div_41 = [
    "Collection, purification and distribution of water (41)",
]
isic_divisions["Collection, purification and distribution of water"] = div_41

####################
# F - Construction #
####################

# Construction

div_45 = ["Construction (45)"]
isic_divisions["Construction"] = div_45

#############################################################
# G - Wholesale and retail trade; repair of motor vehicles, #
# motorcycles and personal and household goods              #
#############################################################

# Sale, maintenance and repair of motor vehicles and motorcycles; retail sale of automotive fuel
div_50 = [
    "Retail sale of automotive fuel",
    "Sale, maintenance, repair of motor vehicles, motor vehicles parts, motorcycles, motor cycles parts and accessoiries",
]
isic_divisions[
    "Sale, maintenance and repair of motor vehicles and motorcycles; retail sale of automotive fuel"
] = div_50

# Wholesale trade and commission trade, except of motor vehicles and motorcycles
div_51 = [
    "Wholesale trade and commission trade, except of motor vehicles and motorcycles (51)",
]
isic_divisions[
    "Wholesale trade and commission trade, except of motor vehicles and motorcycles"
] = div_51

# Retail trade, except of motor vehicles and motorcycles; repair of personal and household goods
div_52 = [
    "Retail trade, except of motor vehicles and motorcycles; repair of personal and household goods (52)",
]
isic_divisions[
    "Retail trade, except of motor vehicles and motorcycles; repair of personal and household goods"
] = div_52

##############################
# H - Hotels and restaurants #
##############################

# Hotels and restaurants
div_55 = ["Hotels and restaurants (55)"]
isic_divisions["Hotels and restaurants"] = div_55

#############################################
# I - Transport, storage and communications #
#############################################

# Land transport; transport via pipelines
div_60 = [
    "Other land transport",
    "Transport via railways",
    "Transport via pipelines",
]
isic_divisions["Land transport; transport via pipelines"] = div_60

# Water transport
div_61 = [
    "Inland water transport",
    "Sea and coastal water transport",
]
isic_divisions["Water transport"] = div_61

# Air transport
div_62 = [
    "Air transport (62)",
]
isic_divisions["Air transport"] = div_62

# Supporting and auxiliary transport activities; activities of travel agencies
div_63 = [
    "Supporting and auxiliary transport activities; activities of travel agencies (63)",
]
isic_divisions[
    "Supporting and auxiliary transport activities; activities of travel agencies"
] = div_63

################################
# J - Financial intermediation #
################################

# Financial intermediation, except insurance and pension funding
div_65 = ["Financial intermediation, except insurance and pension funding (65)"]
isic_divisions["Financial intermediation, except insurance and pension funding"] = (
    div_65
)

# Insurance and pension funding, except compulsory social security
div_66 = ["Insurance and pension funding, except compulsory social security (66)"]
isic_divisions["Insurance and pension funding, except compulsory social security"] = (
    div_66
)

# Activities auxiliary to financial intermediation
div_67 = ["Activities auxiliary to financial intermediation (67)"]
isic_divisions["Activities auxiliary to financial intermediation"] = div_67

####################################################
# K - Real estate, renting and business activities #
####################################################

# Real estate activities
div_70 = [
    "Real estate activities (70)",
]
isic_divisions["Real estate activities"] = div_70

# Renting of machinery and equipment without operator and of personal and household goods
div_71 = [
    "Renting of machinery and equipment without operator and of personal and household goods (71)",
]
isic_divisions[
    "Renting of machinery and equipment without operator and of personal and household goods"
] = div_71

# Research and development
div_73 = [
    "Research and development (73)",
]
isic_divisions["Research and development"] = div_73

# Other business activities
div_74 = [
    "Other business activities (74)",
]
isic_divisions["Other business activities"] = div_74

#####################################################################
# L - Public administration and defence; compulsory social security #
#####################################################################

div_75 = [
    "Public administration and defence; compulsory social security (75)",
]
isic_divisions["Public administration and defence; compulsory social security"] = div_75

#################
# M - Education #
#################

# Education
div_80 = [
    "Education (80)",
]
isic_divisions["Education"] = div_80


##############################
# N - Health and social work #
##############################

# Health and social work
div_85 = ["Health and social work (85)"]
isic_divisions["Health and social work"] = div_85

###############################################################
# O - Other community, social and personal service activities #
###############################################################

# Sewage and refuse disposal, sanitation and similar activities
div_90 = [
    "Incineration of waste: Food",
    "Incineration of waste: Metals and Inert materials",
    "Incineration of waste: Oil/Hazardous waste",
    "Incineration of waste: Paper",
    "Incineration of waste: Plastic",
    "Incineration of waste: Textiles",
    "Incineration of waste: Wood",
    "Landfill of waste: Food",
    "Landfill of waste: Inert/metal/hazardous",
    "Landfill of waste: Paper",
    "Landfill of waste: Plastic",
    "Landfill of waste: Textiles",
    "Landfill of waste: Wood",
    "Waste water treatment, food",
    "Waste water treatment, other",
    "Recycling of bottles by direct reuse",  # Edge case
    "Biogasification of food waste, incl. land application",  # Edge case
    "Biogasification of paper, incl. land application",  # Edge case
    "Biogasification of sewage slugde, incl. land application",  # Edge case
]
isic_divisions["Sewage and refuse disposal, sanitation and similar activities"] = div_90

# Activities of membership organizations n.e.c.
div_91 = [
    "Activities of membership organisation n.e.c. (91)",
]
isic_divisions["Activities of membership organizations n.e.c."] = div_91

# Recreational, cultural and sporting activities
div_92 = ["Recreational, cultural and sporting activities (92)"]
isic_divisions["Recreational, cultural and sporting activities"] = div_92

# Other service activities
div_93 = ["Other service activities (93)"]
isic_divisions["Other service activities"] = div_93

##########################################################################
# P - Activities of private households as employers and undifferentiated #
# production activities of private households                            #
##########################################################################

# Other service activities
div_95 = ["Private households with employed persons (95)"]
isic_divisions["Other service activities"] = div_95

##################################################
# Q - Extra-territorial organizations and bodies #
##################################################

# Extra-territorial organizations and bodies
div_99 = ["Extra-territorial organizations and bodies"]
isic_divisions["Extra-territorial organizations and bodies"] = div_99

########################################################################################


isic_sections = {
    "A - Agriculture, hunting and forestry": div_01 + div_02,
    "B - Fishing": div_05,
    "C - Mining and quarrying": div_10 + div_11 + div_12 + div_13 + div_14,
    "D - Manufacturing": div_15
    + div_16
    + div_17
    + div_18
    + div_19
    + div_20
    + div_21
    + div_22
    + div_23
    + div_24
    + div_25
    + div_26
    + div_27
    + div_28
    + div_29
    + div_31
    + div_33
    + div_34
    + div_35
    + div_36
    + div_37,
    "E - Electricity, gas and water supply": div_40 + div_41,
    "F - Construction": div_45,
    "G - Wholesale and retail trade; repair of motor vehicles, motorcycles and personal and household goods": div_50
    + div_51
    + div_52,
    "H - Hotels and restaurants": div_55,
    "I - Transport, storage and communications": div_60 + div_61 + div_62 + div_63,
    "J - Financial intermediation": div_65 + div_66 + div_67,
    "K - Real estate, renting and business activities": div_70
    + div_71
    + div_73
    + div_74,
    "L - Public administration and defence; compulsory social security": div_75,
    "M - Education": div_80,
    "N - Health and social work": div_85,
    "O - Other community, social and personal service activities": div_90
    + div_91
    + div_92
    + div_93,
    "P - Activities of private households as employers and undifferentiated production activities of private households": div_95,
    "Q - Extra-territorial organizations and bodies": div_99,
}

########################################################################################

ict_industries = [
    "Computer and related activities (72)",
    "Manufacture of office machinery and computers (30)",
    "Manufacture of radio, television and communication equipment and apparatus (32)",
    "Post and telecommunications (64)",
]

mining_industries = [div_10 + div_11 + div_12 + div_13 + div_14]

energy_industries = div_40
