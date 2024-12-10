document.getElementById("analyze").addEventListener("click", async () => {
  const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
  const currentTab = tabs[0];

  const statusEl = document.getElementById("status");
  statusEl.textContent = "Analyzing...";

  try {
    const results = await chrome.scripting.executeScript({
      target: { tabId: currentTab.id },
      func: async () => {
        const colors = {
          hedging: "rgba(255, 255, 0, 0.3)", // Yellow
          extreme: "rgba(255, 165, 0, 0.3)", // Orange
          opinion: "rgba(147, 112, 219, 0.3)", // Purple
          unsubstantiated: "rgba(255, 99, 71, 0.3)", // Tomato
          emotional: {
            positive: "rgba(0, 255, 0, 0.2)", // Light Green
            negative: "rgba(255, 0, 0, 0.2)", // Light Red
          },
        };

        function markdownToHtml(markdown) {
          if (!markdown) return "No comparison with other articles available";

          return markdown
            .replace(/### (.*?)\n/g, "<h3>$1</h3>")
            .replace(/## (.*?)\n/g, "<h2>$1</h2>")
            .replace(/# (.*?)\n/g, "<h1>$1</h1>")
            .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
            .replace(/^\d\. (.*)/gm, "<li>$1</li>")
            .replace(/^- (.*)/gm, "<li>$1</li>")
            .split("\n\n")
            .map((para) => para.trim())
            .filter((para) => para.length > 0)
            .map((para) => {
              if (para.startsWith("<h") || para.startsWith("<li>")) return para;
              return `<p>${para}</p>`;
            })
            .join("\n");
        }

        function getBiasLevel(score) {
          if (score <= 1) return "Minimal bias";
          if (score <= 2) return "Moderate bias";
          if (score <= 3) return "Significant bias";
          return "Heavy bias";
        }

        function getSubjectivityLevel(score) {
          if (score <= 0.25) return "Highly objective";
          if (score <= 0.5) return "Moderately objective";
          if (score <= 0.75) return "Moderately subjective";
          return "Highly subjective";
        }

        function getSentimentLevel(score) {
          if (score < -0.5) return "Very negative";
          if (score < -0.1) return "Slightly negative";
          if (score <= 0.1) return "Neutral";
          if (score <= 0.5) return "Slightly positive";
          return "Very positive";
        }

        function highlightText(text, color, type) {
          console.log("Searching for text:", text);

          const walker = document.createTreeWalker(
            document.body,
            NodeFilter.SHOW_TEXT,
            {
              acceptNode: (node) => {
                if (
                  node.parentElement.closest(
                    "script, style, .article-highlight"
                  )
                ) {
                  return NodeFilter.FILTER_REJECT;
                }
                return NodeFilter.FILTER_ACCEPT;
              },
            }
          );

          let node;
          while ((node = walker.nextNode())) {
            if (node.textContent.includes(text)) {
              const parent = node.parentNode;
              const parts = node.textContent.split(text);
              const container = document.createElement("span");

              for (let i = 0; i < parts.length; i++) {
                // Add text before highlight
                if (parts[i]) {
                  container.appendChild(document.createTextNode(parts[i]));
                }

                // Add highlight if not the last part
                if (i < parts.length - 1) {
                  const highlight = document.createElement("span");
                  highlight.className = "article-highlight";
                  highlight.style.backgroundColor = color;
                  highlight.style.padding = "2px";
                  highlight.style.borderRadius = "2px";
                  highlight.title = type;
                  highlight.textContent = text;
                  container.appendChild(highlight);
                }
              }

              parent.replaceChild(container, node);
            }
          }
        }

        function addHighlights(data) {
          const analysis = data.analysis;

          // Remove existing highlights
          document.querySelectorAll(".article-highlight").forEach((el) => {
            const parent = el.parentNode;
            parent.replaceChild(document.createTextNode(el.textContent), el);
          });

          // Highlight bias indicators
          if (analysis.bias_indicators) {
            analysis.bias_indicators.hedging?.forEach((text) => {
              highlightText(text, colors.hedging, "Hedging Language");
            });

            analysis.bias_indicators.extreme_language?.forEach((text) => {
              highlightText(text, colors.extreme, "Extreme Language");
            });

            analysis.bias_indicators.opinion_statements?.forEach((text) => {
              highlightText(text, colors.opinion, "Opinion Statement");
            });

            analysis.bias_indicators.unsubstantiated_claims?.forEach((text) => {
              highlightText(
                text,
                colors.unsubstantiated,
                "Unsubstantiated Claim"
              );
            });
          }

          // Highlight emotional language
          if (analysis.emotional_language) {
            analysis.emotional_language.forEach((item) => {
              const color =
                item.intensity > 0
                  ? colors.emotional.positive
                  : colors.emotional.negative;
              const type = `Emotional Language`;
              highlightText(item.text, color, type);
            });
          }
        }

        function createAnalysisDisplay(data) {
          const analysis = data.analysis;

          // Remove existing elements
          document
            .querySelectorAll(
              ".article-highlight, .article-analysis-overlay, .highlight-legend"
            )
            .forEach((el) => el.remove());

          const overlay = document.createElement("div");
          overlay.className = "article-analysis-overlay";
          overlay.style.cssText = `
              position: fixed;
              top: 20px;
              right: 20px;
              width: 500px;
              padding: 20px;
              background: white;
              border: 1px solid #ccc;
              border-radius: 5px;
              box-shadow: 0 2px 5px rgba(0,0,0,0.2);
              z-index: 10000;
              font-family: Arial, sans-serif;
              max-height: 90vh;
              display: flex;
              flex-direction: column;
            `;

          const biasScore = analysis.overall_bias_score?.toFixed(2) || "N/A";
          const subjectivityScore =
            (analysis.subjectivity_score * 100)?.toFixed(1) || "N/A";
          const sentimentScore =
            (analysis.sentiment_scores?.compound * 100)?.toFixed(1) || "N/A";

            overlay.innerHTML = `
            <h3 style="margin: 0 0 15px 0;">Article Analysis</h3>
            
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-bottom: 15px;">
              <div>
                <div style="font-weight: 600; font-size: 0.9em; margin-bottom: 5px;">Bias Analysis</div>
                <div style="display: flex; align-items: center; gap: 8px;">
                  <div style="flex-grow: 1; height: 8px; background: #eee; border-radius: 4px;">
                    <div style="width: ${(biasScore/4)*100}%; height: 100%; background: linear-gradient(to right, #4CAF50, #FFC107, #F44336); border-radius: 4px;"></div>
                  </div>
                  <div style="font-size: 0.85em; white-space: nowrap;">${getBiasLevel(biasScore)}</div>
                </div>
              </div>
          
              <div>
                <div style="font-weight: 600; font-size: 0.9em; margin-bottom: 5px;">Subjectivity Level</div>
                <div style="display: flex; align-items: center; gap: 8px;">
                  <div style="flex-grow: 1; height: 8px; background: #eee; border-radius: 4px;">
                    <div style="width: ${subjectivityScore}%; height: 100%; background: linear-gradient(to right, #4CAF50, #F44336); border-radius: 4px;"></div>
                  </div>
                  <div style="font-size: 0.85em; white-space: nowrap;">${getSubjectivityLevel(analysis.subjectivity_score)}</div>
                </div>
              </div>
          
              <div>
                <div style="font-weight: 600; font-size: 0.9em; margin-bottom: 5px;">Overall Sentiment</div>
                <div style="display: flex; align-items: center; gap: 8px;">
                  <div style="flex-grow: 1; height: 8px; background: #eee; border-radius: 4px;">
                    <div style="width: ${Math.abs(sentimentScore)}%; height: 100%; 
                         background: ${sentimentScore >= 0 ? '#4CAF50' : '#F44336'}; 
                         margin-left: ${sentimentScore < 0 ? '50%' : ''}; 
                         margin-right: ${sentimentScore >= 0 ? '50%' : ''}; 
                         border-radius: 4px;"></div>
                  </div>
                  <div style="font-size: 0.85em; white-space: nowrap;">${getSentimentLevel(analysis.sentiment_scores?.compound || 0)}</div>
                </div>
              </div>
          
              <div>
                <div style="font-weight: 600; font-size: 0.9em; margin-bottom: 5px;">Political Leaning</div>
                <div style="font-size: 0.85em;">${data.political_analysis?.leaning || 'N/A'}</div>
              </div>
            </div>
          
            <div style="flex: 1; overflow-y: auto; padding: 15px 0;">
              <div style="font-weight: bold; margin-bottom: 10px;">Article Comparison</div>
              <div style="font-size: 0.9em; line-height: 1.6;">
                ${markdownToHtml(data.GPT_Compare)}
              </div>
            </div>
          
            <div style="margin-top: 10px; border-top: 1px solid #eee; padding-top: 10px;">
              <div style="font-weight: bold; margin-bottom: 8px;">Related Articles</div>
              <div style="overflow-x: auto; white-space: nowrap; margin: 0 -5px;">
                ${data.related_articles?.map(article => `
                  <div style="
                    display: inline-block;
                    vertical-align: top;
                    width: 200px;
                    margin: 0 5px;
                    padding: 8px;
                    border: 1px solid #eee;
                    border-radius: 4px;
                    background: #f8f9fa;
                    white-space: normal;
                  ">
                    <div style="font-weight: 600; font-size: 0.85em; margin-bottom: 5px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
                      ${article.title || 'Untitled'}
                    </div>
                    <div style="color: #666; font-size: 0.75em; margin-bottom: 5px;">
                      ${article.source?.name || 'Unknown Source'} - ${new Date(article.publishedAt).toLocaleDateString()}
                    </div>
                    <a href="${article.url}" target="_blank" style="
                      display: inline-block;
                      padding: 3px 6px;
                      background: #f0f0f0;
                      border-radius: 3px;
                      text-decoration: none;
                      color: #666;
                      font-size: 0.75em;
                    ">Read More</a>
                  </div>
                `).join('') || 'No related articles available'}
              </div>
            </div>
          
            <div style="text-align: right; margin-top: 10px;">
              <button onclick="this.parentElement.parentElement.remove()" style="
                padding: 4px 8px;
                border: none;
                background: #f0f0f0;
                border-radius: 3px;
                cursor: pointer;
              ">Close</button>
            </div>
          `;

          document.body.appendChild(overlay);

          // Add legend
          const legend = document.createElement("div");
          legend.className = "highlight-legend";
          legend.style.cssText = `
              position: fixed;
              top: 20px;
              left: 20px;
              background: white;
              padding: 15px;
              border: 1px solid #ccc;
              border-radius: 5px;
              box-shadow: 0 2px 5px rgba(0,0,0,0.2);
              z-index: 10000;
              font-family: Arial, sans-serif;
            `;
          legend.innerHTML = `
              <h4 style="margin: 0 0 10px 0">Highlight Legend</h4>
              ${Object.entries({
                "Extreme Language": colors.extreme,
                "Hedging Language": colors.hedging,
                "Opinion Statements": colors.opinion,
                "Unsubstantiated Claims": colors.unsubstantiated,
                "Positive Emotional": colors.emotional.positive,
                "Negative Emotional": colors.emotional.negative,
              })
                .map(
                  ([label, color]) => `
                <div style="margin-bottom: 5px; display: flex; align-items: center;">
                  <span style="display: inline-block; width: 15px; height: 15px; background: ${color}; margin-right: 5px;"></span>
                  ${label}
                </div>
              `
                )
                .join("")}
              <div style="margin-top: 10px;">
                <button onclick="this.parentElement.parentElement.remove()">Close</button>
              </div>
            `;

          document.body.appendChild(legend);
          return true;
        }

        try {
          const response = await fetch(
            "https://cs489-newsperspective-backend-production.up.railway.app/api/analyze",
            {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ article_text: document.body.innerText }),
            }
          );

          const data = await response.json();
          if (!data || !data.analysis) {
            throw new Error("Invalid API response format");
          }

          const displayAdded = createAnalysisDisplay(data);
          addHighlights(data);

          return { success: true, displayAdded };
        } catch (error) {
          console.error("Error:", error);
          return { success: false, error: error.message };
        }
      },
    });

    const result = results[0].result;
    if (result.success) {
      statusEl.textContent = "Analysis complete!";
    } else {
      throw new Error(result.error);
    }
  } catch (error) {
    statusEl.textContent = "Error: " + error.message;
  }
});
