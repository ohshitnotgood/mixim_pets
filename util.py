def generate_weights(number_layer, number_mix_per_layer):
    probability = []
    for i in range(number_layer):
        probab_tem = []
        for j in range(number_mix_per_layer):
            probab_tem.append((1) / (number_mix_per_layer))
        probability.append(probab_tem)
    return probability
