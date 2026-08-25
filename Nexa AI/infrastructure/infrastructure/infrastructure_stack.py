from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    CfnOutput,
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_lambda as lambda_,
    aws_apigatewayv2 as apigwv2,
    aws_apigatewayv2_integrations as integrations,
    aws_iam as iam,
)


from constructs import Construct


class InfrastructureStack(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs
    ) -> None:

        super().__init__(scope, construct_id, **kwargs)

        # ============================================================
        # 1. FRONTEND S3 BUCKET
        # ============================================================

        frontend_bucket = s3.Bucket(
            self,
            "NexaFrontendBucket",

            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,

            encryption=s3.BucketEncryption.S3_MANAGED,

            enforce_ssl=True,

            removal_policy=RemovalPolicy.DESTROY,

            auto_delete_objects=True,
        )

        # ============================================================
        # 2. BACKEND LAMBDA
        # ============================================================

        backend_lambda = lambda_.Function(
            self,
            "NexaBackendLambda",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="main.handler",
            code=lambda_.Code.from_asset("../backend/package"),
            timeout=Duration.seconds(60),
            memory_size=1024,
        )

        # ============================================================
        # 3. BEDROCK PERMISSION
        # ============================================================

        backend_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream",
                ],
                resources=["*"],
            )
        )

        # ============================================================
        # 4. API GATEWAY HTTP API
        # ============================================================

        api = apigwv2.HttpApi(
            self,
            "NexaHttpApi",

            api_name="Nexa-AI-API",

            cors_preflight=apigwv2.CorsPreflightOptions(
                allow_origins=["*"],

                allow_methods=[
                    apigwv2.CorsHttpMethod.POST,
                    apigwv2.CorsHttpMethod.OPTIONS,
                ],

                allow_headers=["*"],
            ),
        )

        # Lambda integration

        integration = integrations.HttpLambdaIntegration(
            "NexaLambdaIntegration",
            backend_lambda,
        )

        # /chat endpoint

        api.add_routes(
            path="/chat",

            methods=[
                apigwv2.HttpMethod.POST
            ],

            integration=integration,
        )

        # ============================================================
        # 5. CLOUDFRONT
        # ============================================================

        distribution = cloudfront.Distribution(
            self,
            "NexaCloudFrontDistribution",

            comment="Nexa AI Frontend Distribution",

            default_root_object="index.html",

            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3BucketOrigin.with_origin_access_control(
                    frontend_bucket
                ),

                viewer_protocol_policy=(
                    cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS
                ),

                allowed_methods=(
                    cloudfront.AllowedMethods.ALLOW_GET_HEAD
                ),

                cached_methods=(
                    cloudfront.CachedMethods.CACHE_GET_HEAD
                ),

                compress=True,
            ),

            price_class=cloudfront.PriceClass.PRICE_CLASS_100,

            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=404,

                    response_http_status=200,

                    response_page_path="/index.html",

                    ttl=Duration.seconds(0),
                )
            ],
        )

        # ============================================================
        # 6. UPLOAD FRONTEND TO S3
        # ============================================================

        s3deploy.BucketDeployment(
            self,
            "NexaFrontendDeployment",

            sources=[
                s3deploy.Source.asset("../frontend")
            ],

            destination_bucket=frontend_bucket,

            distribution=distribution,

            distribution_paths=["/*"],
        )

        # ============================================================
        # 7. OUTPUTS
        # ============================================================

        CfnOutput(
            self,
            "FrontendBucketName",

            value=frontend_bucket.bucket_name,

            description="Nexa AI Frontend S3 Bucket",
        )

        CfnOutput(
            self,
            "CloudFrontURL",

            value=f"https://{distribution.domain_name}",

            description="Nexa AI CloudFront URL",
        )

        CfnOutput(
            self,
            "ApiURL",

            value=api.api_endpoint,

            description="Nexa AI API Gateway URL",
        )

        CfnOutput(
            self,
            "ChatEndpoint",

            value=f"{api.api_endpoint}/chat",

            description="Nexa AI Chat API Endpoint",
        )