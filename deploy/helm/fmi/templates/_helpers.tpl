{{/*
Expand the name of the chart.
*/}}
{{- define "fmi.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "fmi.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{- define "fmi.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "fmi.labels" -}}
helm.sh/chart: {{ include "fmi.chart" . }}
{{ include "fmi.selectorLabels" . }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "fmi.selectorLabels" -}}
app.kubernetes.io/name: {{ include "fmi.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "fmi.api.fullname" -}}
{{- printf "%s-api" (include "fmi.fullname" .) }}
{{- end }}

{{- define "fmi.frontend.fullname" -}}
{{- printf "%s-frontend" (include "fmi.fullname" .) }}
{{- end }}

{{- define "fmi.postgres.fullname" -}}
{{- printf "%s-postgres" (include "fmi.fullname" .) }}
{{- end }}

{{- define "fmi.valkey.fullname" -}}
{{- printf "%s-valkey" (include "fmi.fullname" .) }}
{{- end }}

{{- define "fmi.secretName" -}}
{{- printf "%s-secrets" (include "fmi.fullname" .) }}
{{- end }}

{{- define "fmi.configMapName" -}}
{{- printf "%s-config" (include "fmi.fullname" .) }}
{{- end }}

{{/*
Image reference with optional registry prefix.
*/}}
{{- define "fmi.image" -}}
{{- $registry := .global.imageRegistry | default "" -}}
{{- if $registry -}}
{{- printf "%s%s:%s" $registry .repository .tag -}}
{{- else -}}
{{- printf "%s:%s" .repository .tag -}}
{{- end -}}
{{- end }}

{{- define "fmi.databaseUrl" -}}
{{- if .Values.secrets.databaseUrl -}}
{{- .Values.secrets.databaseUrl -}}
{{- else if .Values.externalDatabase.url -}}
{{- .Values.externalDatabase.url -}}
{{- else if .Values.postgres.enabled -}}
{{- $user := .Values.postgres.auth.username -}}
{{- $pass := .Values.secrets.postgresPassword | default .Values.postgres.auth.password -}}
{{- if not $pass -}}
{{- fail "Set secrets.postgresPassword (or postgres.auth.password) for in-cluster Postgres — never commit real secrets" -}}
{{- end -}}
{{- $db := .Values.postgres.auth.database -}}
{{- $host := include "fmi.postgres.fullname" . -}}
{{- printf "postgresql+psycopg://%s:%s@%s:5432/%s" $user $pass $host $db -}}
{{- else -}}
{{- fail "Set postgres.enabled=true with secrets.postgresPassword, or secrets.databaseUrl / externalDatabase.url" -}}
{{- end -}}
{{- end }}


{{- define "fmi.redisUrl" -}}
{{- if .Values.externalValkey.url -}}
{{- .Values.externalValkey.url -}}
{{- else if .Values.valkey.enabled -}}
{{- printf "redis://%s:6379/0" (include "fmi.valkey.fullname" .) -}}
{{- else -}}
{{- fail "Set valkey.enabled=true or externalValkey.url" -}}
{{- end -}}
{{- end }}

{{- define "fmi.frontend.internalApiUrl" -}}
{{- if .Values.frontend.internalApiUrl -}}
{{- .Values.frontend.internalApiUrl -}}
{{- else -}}
{{- printf "http://%s:%v" (include "fmi.api.fullname" .) .Values.api.service.port -}}
{{- end -}}
{{- end }}
