<template>
  <div class="min-h-screen bg-emerald-50 py-10 px-4">
    <div class="max-w-4xl mx-auto">

      <!-- En-tête -->
      <div class="text-center mb-10">
        <h1 class="text-3xl font-extrabold text-emerald-900 sm:text-4xl">
          AgriTech Recommander CI
        </h1>
        <p class="mt-2 text-lg text-emerald-700">
          Système intelligent d'aide à la décision pour le choix des cultures locales
        </p>
      </div>

      <!-- Message d'erreur -->
      <div v-if="erreur" class="mb-6 p-4 bg-red-100 border-l-4 border-red-500 text-red-700 rounded shadow-sm">
        <p class="font-bold">Erreur de connexion</p>
        <p>{{ erreur }}</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">

        <!-- Formulaire -->
        <div class="bg-white p-6 rounded-2xl shadow-xl border border-emerald-100">
          <h2 class="text-xl font-bold text-gray-800 mb-6 border-b pb-2 flex items-center gap-2">
            Paramètres du Sol & Climat
          </h2>

          <div class="space-y-4">
            <div class="grid grid-cols-3 gap-3">
              <div>
                <label class="block text-xs font-semibold text-gray-600 uppercase">Azote (N)</label>
                <input type="number" v-model="form.N"
                  class="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 shadow-sm focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500" />
              </div>
              <div>
                <label class="block text-xs font-semibold text-gray-600 uppercase">Phosphore (P)</label>
                <input type="number" v-model="form.P"
                  class="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 shadow-sm focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500" />
              </div>
              <div>
                <label class="block text-xs font-semibold text-gray-600 uppercase">Potassium (K)</label>
                <input type="number" v-model="form.K"
                  class="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 shadow-sm focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500" />
              </div>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700">Température (°C)</label>
                <input type="number" step="0.1" v-model="form.temperature"
                  class="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 shadow-sm focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">Humidité (%)</label>
                <input type="number" step="0.1" v-model="form.humidity"
                  class="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 shadow-sm focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500" />
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">pH du sol (0 à 14)</label>
              <input type="number" step="0.1" v-model="form.ph"
                class="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 shadow-sm focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500" />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">Précipitations (mm/an)</label>
              <input type="number" step="0.1" v-model="form.rainfall"
                class="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 shadow-sm focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500" />
            </div>

            <button
              @click="lancer"
              :disabled="chargement"
              class="w-full mt-4 bg-emerald-600 text-white py-3 px-4 rounded-xl font-bold hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 transition-all disabled:opacity-50">
              {{ chargement ? 'Analyse en cours...' : 'Lancer la Recommandation' }}
            </button>
          </div>
        </div>

        <!-- Résultats -->
        <div class="bg-white p-6 rounded-2xl shadow-xl border border-emerald-100 flex flex-col justify-between">
          <div>
            <h2 class="text-xl font-bold text-gray-800 mb-6 border-b pb-2">
              Résultat de la Prédiction
            </h2>

            <!-- État vide -->
            <div v-if="!resultat" class="text-center py-12 text-gray-400">
              <span class="text-5xl block mb-2"></span>
              Saisissez les données du sol à gauche et lancez l'analyse pour voir la culture recommandée.
            </div>

            <!-- Résultats -->
            <div v-else class="space-y-6">

              <!-- Culture recommandée -->
              <div class="bg-emerald-50 p-6 rounded-xl text-center border border-emerald-200">
                <span class="text-sm font-semibold text-emerald-800 uppercase tracking-wider">Culture Idéale Détectée</span>
                <h3 class="text-3xl font-black text-emerald-600 mt-2 uppercase">
                  {{ resultat.culture_recommandee }}
                </h3>
              </div>

              <!-- Barre de confiance -->
              <div class="bg-gray-50 p-4 rounded-lg">
                <div class="flex justify-between text-sm font-medium text-gray-600 mb-2">
                  <span>Indice de confiance</span>
                  <span class="font-bold text-gray-900">{{ resultat.confiance.toFixed(1) }}%</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
                  <div class="bg-emerald-500 h-2 rounded-full transition-all duration-700"
                    :style="{ width: resultat.confiance + '%' }">
                  </div>
                </div>
              </div>

              <!-- Détail des probabilités -->
              <div class="space-y-2">
                <span class="text-xs font-semibold text-gray-600 uppercase tracking-wider">Détail des probabilités</span>
                <div v-for="(proba, culture) in resultat.toutes_probabilites" :key="culture"
                  class="flex items-center gap-2">
                  <span class="text-xs w-24 text-gray-700 capitalize">{{ culture }}</span>
                  <div class="flex-1 bg-gray-200 rounded-full h-2">
                    <div class="bg-emerald-400 h-2 rounded-full transition-all duration-500"
                      :style="{ width: proba + '%' }">
                    </div>
                  </div>
                  <span class="text-xs font-mono w-10 text-right text-gray-600">{{ proba }}%</span>
                </div>
              </div>

            </div>
          </div>

          <!-- Dernière analyse -->
          <div v-if="derniereAnalyse" class="mt-6 pt-4 border-t text-xs text-gray-500 grid grid-cols-2 gap-1">
            <span>Dernière analyse :</span>
            <span class="text-right font-mono">
              N:{{ derniereAnalyse.N }} | P:{{ derniereAnalyse.P }} | K:{{ derniereAnalyse.K }}
            </span>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

// État du formulaire avec valeurs par défaut réalistes (profil cacao CI)
const form = reactive({
  N: 45,
  P: 55,
  K: 40,
  temperature: 26.5,
  humidity: 82,
  ph: 6.5,
  rainfall: 1700
})

const resultat = ref(null)
const erreur = ref(null)
const chargement = ref(false)
const derniereAnalyse = ref(null)

// Appel direct vers FastAPI — plus besoin de passer par Laravel
const lancer = async () => {
  erreur.value = null
  chargement.value = true

  try {
    const response = await fetch('http://127.0.0.1:8000/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        N: Number(form.N),
        P: Number(form.P),
        K: Number(form.K),
        temperature: Number(form.temperature),
        humidity: Number(form.humidity),
        ph: Number(form.ph),
        rainfall: Number(form.rainfall)
      })
    })

    if (!response.ok) {
      throw new Error(`Erreur API : ${response.status}`)
    }

    resultat.value = await response.json()
    derniereAnalyse.value = { ...form }

  } catch (e) {
    erreur.value = 'Impossible de joindre le serveur de prédiction. Vérifie que FastAPI tourne sur le port 8000.'
    resultat.value = null
  } finally {
    chargement.value = false
  }
}
</script>