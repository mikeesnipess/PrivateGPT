import torch
import ollama
import os
import json

class OllamaChatService:
    PINK = '\033[95m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    NEON_GREEN = '\033[92m'
    RESET_COLOR = '\033[0m'

    def __init__(self, model="llama3", vault_file_path="vault.txt"):
        self.model = model
        self.vault_file_path = vault_file_path
        self.vault_content = self._load_vault_content()
        self.vault_embeddings_tensor = self._generate_vault_embeddings()
        self.conversation_history = []
        self.system_message = ("Ești un asistent util care este expert în extragerea celor mai utile "
                               "informații dintr-un text dat. De asemenea, adu informații suplimentare relevante "
                               "pentru interogarea utilizatorului din afara contextului dat.")

    def _load_vault_content(self):
        print(self.NEON_GREEN + "Loading vault content..." + self.RESET_COLOR)
        if os.path.exists(self.vault_file_path):
            with open(self.vault_file_path, "r", encoding='utf-8') as vault_file:
                return vault_file.readlines()
        return []

    def _generate_vault_embeddings(self):
        print(self.NEON_GREEN + "Generating embeddings for the vault content..." + self.RESET_COLOR)
        vault_embeddings = []
        for content in self.vault_content:
            response = ollama.embeddings(model='mxbai-embed-large', prompt=content)
            vault_embeddings.append(response["embedding"])
        return torch.tensor(vault_embeddings)

    def _get_relevant_context(self, rewritten_input, top_k=3):
        if self.vault_embeddings_tensor.nelement() == 0:
            return []
        input_embedding = ollama.embeddings(model='mxbai-embed-large', prompt=rewritten_input)["embedding"]
        cos_scores = torch.cosine_similarity(torch.tensor(input_embedding).unsqueeze(0), self.vault_embeddings_tensor)
        top_k = min(top_k, len(cos_scores))
        top_indices = torch.topk(cos_scores, k=top_k)[1].tolist()
        relevant_context = [self.vault_content[idx].strip() for idx in top_indices]
        return relevant_context

    def _rewrite_query(self, user_input_json):
        user_input = json.loads(user_input_json)["Query"]
        context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.conversation_history[-2:]])
        prompt = (f"Rescrie următoarea interogare integrând contextul relevant din istoricul conversației. "
                  f"Interogarea rescrisă ar trebui să:\n\n"
                  f"- Păstreze intenția și sensul esențial al interogării originale\n"
                  f"- Expandeze și clarifice interogarea pentru a o face mai specifică și informativă pentru obținerea contextului relevant\n"
                  f"- Evite introducerea de noi subiecte sau întrebări care se abate de la interogarea originală\n"
                  f"- NU RĂSPUNDE NICIODATĂ la interogarea originală, ci concentrează-te pe reformularea și extinderea acesteia într-o nouă interogare\n\n"
                  f"Istoric conversație:\n{context}\n\n"
                  f"Interogare originală: [{user_input}]\n\n"
                  f"Interogare rescrisă:")
        response = ollama.chat(
            model=self.model,
            messages=[{"role": "system", "content": prompt}]
        )
        rewritten_query = response['message']['content'].strip()
        return json.dumps({"Rewritten Query": rewritten_query})

    def chat(self, user_input):
        self.conversation_history.append({"role": "user", "content": user_input})

        if len(self.conversation_history) > 1:
            query_json = {
                "Query": user_input,
                "Rewritten Query": ""
            }
            rewritten_query_json = self._rewrite_query(json.dumps(query_json))
            rewritten_query_data = json.loads(rewritten_query_json)
            rewritten_query = rewritten_query_data["Rewritten Query"]
            print(self.PINK + "Interogare originală: " + user_input + self.RESET_COLOR)
            print(self.PINK + "Interogare rescrisă: " + rewritten_query + self.RESET_COLOR)
        else:
            rewritten_query = user_input

        relevant_context = self._get_relevant_context(rewritten_query)
        if relevant_context:
            context_str = "\n".join(relevant_context)
            print("Context extras din documente: \n\n" + self.CYAN + context_str + self.RESET_COLOR)
        else:
            print(self.CYAN + "Nu s-a găsit niciun context relevant." + self.RESET_COLOR)

        user_input_with_context = user_input
        if relevant_context:
            user_input_with_context = user_input + "\n\nContext relevant:\n" + context_str

        self.conversation_history[-1]["content"] = user_input_with_context

        messages = [
            {"role": "system", "content": self.system_message},
            *self.conversation_history
        ]

        response = ollama.chat(
            model=self.model,
            messages=messages
        )

        print("Răspuns complet:", response)

        assistant_content = response.get('message', {}).get('content', 'Nu s-a găsit text de răspuns')
        self.conversation_history.append({"role": "assistant", "content": assistant_content})

        return assistant_content

