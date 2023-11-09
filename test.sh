docker pull $CI_REGISTRY_IMAGE -a
TAG=$(docker images --format "{{.Tag}}" | sort -r -n | head -1)
last_element=$(echo "$TAG" | cut -d'.' -f3)
previous_elements=$(echo "$TAG" | cut -d'.' -f1-2)
incremented_last_element=$((last_element + 1))
NEW_TAG="$previous_elements.$incremented_last_element"
echo $NEW_TAG