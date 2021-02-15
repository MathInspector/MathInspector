#version 330 core

uniform vec3 lightPos;

in vec2 fragCoord;
in vec3 normal;
in vec4 fragPos;
out vec4 fragColor;

void main()
{
	vec3 objectColor = vec3(0.776,0.3647,0.352);
	if (fragCoord.x < 0.01 || fragCoord.x > 0.99 || fragCoord.y < 0.01 || fragCoord.y > 0.99) {
		objectColor = vec3(0.6862, 0.4901, 1.0);
	}

	vec3 lightColor = vec3(1);
	float ambientStrength = 0.5;

	vec3 lightDir = normalize(lightPos - fragPos.xyz);
	float diff = max(dot(normal, lightDir), 0.0);
	vec3 diffuse = diff * lightColor;

	vec3 ambient = ambientStrength*lightColor;
	vec3 result = (ambient + diffuse) * objectColor;
	fragColor = vec4(result, 1.0);

}