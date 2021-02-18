#version 330 core

precision highp float;

#define fragCoord gl_FragCoord.xy

uniform mat4 model;
uniform mat4 view;
uniform mat4 proj;
uniform float zoom;
uniform vec3 cameraPos;

in vec3 nearPoint;
in vec3 farPoint;
out vec4 fragColor;

vec4 grid(vec3 R, float scale) {
	vec2 deriv = fwidth(R.xy);
	vec3 gv = fract(R);
	vec3 ggv = fract(R/10);
	float z = abs(cameraPos.z/zoom);
    float delta = 0.02;

	vec3 color = vec3(0);
	float opacity = 0;


    float X = smoothstep(-delta, 0, R.x) - smoothstep(0, delta, R.x);
    float Y = smoothstep(-delta,0, R.z) - smoothstep(0, delta, R.z);

    float x = smoothstep(delta, 0, gv.x) + smoothstep(1-delta, 1, gv.x);
    float y = smoothstep(delta, 0, gv.z) + smoothstep(1-delta, 1, gv.z);

    float xx = smoothstep(delta/5, 0, ggv.x);
    float yy = smoothstep(delta/5, 0, ggv.z);

    if (X > 0) {
	    // color = vec3(1,0,0);
	    color = vec3(0.7803921568627451, 0.796078431372549, 0.8196078431372549);
	    // color = vec3(0.6431372549019608, 0.8941176470588236, 0.0196078431372549);
	    opacity = 1;
	} else if (Y > 0) {
	    // color = vec3(0,1,0);
	    color = vec3(0.7803921568627451, 0.796078431372549, 0.8196078431372549);
	    // color = vec3(0.9882352941176471, 0.11764705882352941, 0.4392156862745098);
	    opacity = 1;
	} else if (x > 0 || y > 0) {
	    color = vec3(0.4);
	    opacity = 1;

		// if (z > 25) {
		// 	opacity = clamp(1 - (z - 25)/25, 0, 1);
		// } else {
		// 	opacity = 1;
		// }
    } else if (xx > 0 || yy > 0) {
	    color = vec3(0.4);
	    opacity = 1;

		// if (z > 125) {
		// 	opacity = clamp(1 - (z - 125)/100, 0, 1);
		// } else {
		// 	opacity = 0.9;
		// }
    }

	vec4 result = vec4(color, opacity);

	return result;
}

float computeDepth(vec3 pos) {
	vec4 clip_space_pos = proj * view * model * vec4(pos.xyz, 1.0);
	float clip_space_depth = clip_space_pos.z / clip_space_pos.w;

	float far = gl_DepthRange.far;
	float near = gl_DepthRange.near;

	float depth = (((far-near) * clip_space_depth) + near + far) / 2.0;

	return depth;
}

float computeLinearDepth(vec3 pos) {
    vec4 clip_space_pos = proj * view * model * vec4(pos.xyz, 1.0);
    float clip_space_depth = (clip_space_pos.z / clip_space_pos.w) * 2.0 - 1.0;
    float near = 0.1;
    float far = 100;
    float result = (near * far) / (far + near - clip_space_depth * (far - near));
    return result / far;
}

void main()
{
	float t = -nearPoint.y / (farPoint.y-nearPoint.y);
	vec3 R = nearPoint + t * (farPoint-nearPoint);

	vec4 color = grid(R,1);

	float linearDepth = computeLinearDepth(R);
    float fading = max(0, (0.8 - linearDepth));

	gl_FragDepth = computeDepth(R);

	fragColor = color * float(t > 0);
	fragColor *= fading;
}
