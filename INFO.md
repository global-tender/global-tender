requires:
```
pyyaml
ua-parser
user-agents
django-user-agents
```

Ways to modify images or pdf before publishing:
```

for img in *; do convert "$img" -resize "512" "sml_${img}"; done

convert -density 300 -trim test.pdf -quality 100 test.jpg

```