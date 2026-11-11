package main

import (
	"fmt"
	"log"
	"net/http"

	"github.com/casbin/casbin/v2"
	"github.com/gin-gonic/gin"
)

// CasbinMiddleware valida permissões ABAC/RBAC dinamicamente
func CasbinMiddleware(e *casbin.Enforcer) gin.HandlerFunc {
	return func(c *gin.Context) {
		// Extrai o usuário e tenant dos headers (injetados pelo API Gateway)
		sub := c.GetHeader("X-User-Role")   // ex: "driver", "logistics_manager", "auditor"
		domain := c.GetHeader("X-Tenant-ID") // ex: "carrier_alpha"
		obj := c.Request.URL.Path           // ex: "/api/v1/shipment/reroute"
		act := c.Request.Method             // ex: "POST"

		// Avaliação no Engine do Casbin
		allowed, err := e.Enforce(sub, domain, obj, act)
		if err != nil {
			c.AbortWithStatusJSON(http.StatusInternalServerError, gin.H{"error": "Erro ao avaliar autorização"})
			return
		}

		if !allowed {
			c.AbortWithStatusJSON(http.StatusForbidden, gin.H{
				"error": fmt.Sprintf("Acesso negado para o papel '%s' no recurso '%s'", sub, obj),
			})
			return
		}

		c.Next()
	}
}

func main() {
	// Inicializa o Enforcer com os arquivos de modelo e política
	enforcer, err := casbin.NewEnforcer("config/rbac_tenant_model.conf", "config/policy.csv")
	if err != nil {
		log.Fatalf("Falha ao inicializar o Casbin: %v", err)
	}

	r := gin.Default()
	r.Use(CasbinMiddleware(enforcer))

	r.POST("/api/v1/shipment/reroute", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "Rota alterada com sucesso."})
	})

	log.Println("Servidor de Segurança Logística rodando na porta 8080...")
	r.Run(":8080")
}
